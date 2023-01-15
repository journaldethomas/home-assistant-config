import voluptuous as vol
import logging
from typing import Any, Optional
from oauthlib.oauth2 import rfc6749

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow, FlowResult

from .const import DOMAIN
from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SENSORS,
    CONF_ENEDIS_LOAD_SHEDDING,
    CONF_SENSOR_UNIT,
    CONF_SENSOR_SHIFT,
)
from . import AsyncOauthClient

_LOGGER = logging.getLogger(__name__)

# Description of the config flow:
# async_step_user is called when user starts to configure the integration
# we follow with a flow of form/menu
# eventually we call async_create_entry with a dictionnary of data
# HA calls async_setup_entry with a ConfigEntry which wraps this data (defined in __init__.py)
# in async_setup_entry we call hass.config_entries.async_setup_platforms to setup each relevant platform (sensor in our case)
# HA calls async_setup_entry from sensor.py


class SetupConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Called once with None as user_input, then a second time with user provided input"""
        errors = {}
        valid = False

        if user_input is not None:
            _LOGGER.debug(f"User input is {user_input}")
            _LOGGER.debug("Testing connectivity to RTE api")
            try:
                test_client = AsyncOauthClient(user_input)
                await test_client.client()
                valid = True
            except rfc6749.errors.InvalidClientError:
                _LOGGER.error(
                    "Unable to validate RTE api access. Credentials are likely incorrect"
                )
                errors["base"] = "auth_error"
            except Exception as e:
                _LOGGER.error(f"Unable to validate RTE api access, unknown error: {e}")
                errors["base"] = "generic_error"
            if valid:
                _LOGGER.debug("Connectivity to RTE api validated")
                self.user_input = user_input
                if "sensors" not in self.user_input:
                    self.user_input["sensors"] = []
                if CONF_ENEDIS_LOAD_SHEDDING not in self.user_input:
                    self.user_input[CONF_ENEDIS_LOAD_SHEDDING] = [False]

                return self._configuration_menu("user")

        data_schema = {
            vol.Required(CONF_CLIENT_ID): cv.string,
            vol.Required(CONF_CLIENT_SECRET): cv.string,
        }

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )

    def _configuration_menu(self, step_id: str):
        return self.async_show_menu(
            step_id=step_id,
            menu_options=[
                "finish_configuration",
            ],
        )

    async def async_step_finish_configuration(
        self, user_input: Optional[dict[str, Any]] = None
    ):
        _LOGGER.info(f"Configuration from user is finished, input is {self.user_input}")
        await self.async_set_unique_id(self.user_input[CONF_CLIENT_ID])
        self._abort_if_unique_id_configured()
        # will call async_setup_entry defined in __init__.py file
        return self.async_create_entry(title="ecowatt by RTE", data=self.user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


# FIXME(g.seux): This class is mostly a duplicate from the SetupConfigFlow. How can we make it common
class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.user_input = None

    async def async_step_init(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""

        if self.user_input is None:  # done once, feed user_input with existing sensors
            self.user_input: dict[
                str, Any
            ] = self.config_entry.data  # casting is a bit brutal but works

        return self._configuration_menu("init")

    def _configuration_menu(self, step_id: str):
        return self.async_show_menu(
            step_id=step_id,
            menu_options=[
                "finish_configuration",
                "configure_hours_sensor",
                "configure_days_sensor",
                "enable_load_shedding_announcements",
            ],
        )

    async def async_step_enable_load_shedding_announcements(
        self, user_input: Optional[dict[str, Any]] = None
    ):
        step_name = f"enable_load_shedding_announcements"
        errors = {}
        data_schema = {vol.Required(CONF_ENEDIS_LOAD_SHEDDING): vol.Coerce(bool)}
        if user_input is not None:
            self.user_input[CONF_ENEDIS_LOAD_SHEDDING][0] = user_input[
                CONF_ENEDIS_LOAD_SHEDDING
            ]
            return self._configuration_menu(step_name)

        return self.async_show_form(
            step_id=step_name,
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

    async def async_step_finish_configuration(
        self, user_input: Optional[dict[str, Any]] = None
    ):
        _LOGGER.info(f"Configuration from user is finished, input is {self.user_input}")
        # will call async_setup_entry defined in __init__.py file
        return self.async_create_entry(title="ecowatt by RTE", data=self.user_input)

    async def async_step_configure_hours_sensor(
        self, user_input: Optional[dict[str, Any]] = None
    ):
        return self._manual_configuration_step(
            "hours", vol.In(range(3 * 24)), user_input
        )

    async def async_step_configure_days_sensor(
        self, user_input: Optional[dict[str, Any]] = None
    ):
        return self._manual_configuration_step("days", vol.In(range(4)), user_input)

    def _manual_configuration_step(
        self, sensor_unit, validator, user_input: Optional[dict[str, Any]] = None
    ):
        step_name = f"configure_{sensor_unit}_sensor"
        errors = {}
        data_schema = {
            vol.Required(CONF_SENSOR_SHIFT): vol.All(vol.Coerce(int), validator),
        }
        if user_input is not None:
            self.user_input["sensors"].append(
                {
                    CONF_SENSOR_UNIT: sensor_unit,
                    CONF_SENSOR_SHIFT: user_input[CONF_SENSOR_SHIFT],
                }
            )
            return self._configuration_menu(step_name)

        return self.async_show_form(
            step_id=step_name,
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )
