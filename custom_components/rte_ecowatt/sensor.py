import voluptuous as vol
from datetime import timedelta, datetime
from typing import Optional
import logging
import asyncio

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
)
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityPlatformState
from homeassistant.config_entries import ConfigEntry

from . import (
    HourlyEcowattLevel,
    DailyEcowattLevel,
    ElectricityDistributorEntity,
    DetectedAddress,
)
from .const import (
    DOMAIN,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_ENEDIS_LOAD_SHEDDING,
    CONF_SENSOR_UNIT,
    CONF_SENSOR_SHIFT,
    CONF_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SENSOR_UNIT): vol.All(cv.string, vol.In(["days", "hours"])),
        vol.Required(CONF_SENSOR_SHIFT): vol.Coerce(int),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_ENEDIS_LOAD_SHEDDING): vol.All(cv.ensure_list, [cv.boolean]),
        vol.Required(CONF_SENSORS, default=[]): vol.All(
            cv.ensure_list, [SENSOR_SCHEMA]
        ),
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    _LOGGER.info("Called async setup entry")
    rte_coordinator = hass.data[DOMAIN][entry.entry_id]["rte_coordinator"]
    enedis_coordinator = hass.data[DOMAIN][entry.entry_id]["enedis_coordinator"]
    sensors = []
    sensors.append(DailyEcowattLevel(rte_coordinator, 0, hass))
    sensors.append(HourlyEcowattLevel(rte_coordinator, 0, hass))

    for sensor_config in entry.data[CONF_SENSORS]:
        if sensor_config[CONF_SENSOR_UNIT] == "days":
            klass = DailyEcowattLevel
        elif sensor_config[CONF_SENSOR_UNIT] == "hours":
            klass = HourlyEcowattLevel
        else:
            raise Exception("Unknown sensor unit type")
        sensors.append(klass(rte_coordinator, sensor_config[CONF_SENSOR_SHIFT], hass))

    if entry.data[CONF_ENEDIS_LOAD_SHEDDING][
        0
    ]:  # this sensor transmit PII to external provider, it's opt-in
        sensors.append(ElectricityDistributorEntity(enedis_coordinator, hass))
        sensors.append(DetectedAddress(enedis_coordinator, hass))

    async_add_entities(sensors)
    while not all(
        s.restored for s in sensors if s._platform_state == EntityPlatformState.ADDED
    ):
        _LOGGER.debug(f"Wait for all {len(sensors)} sensors to have been restored")
        await asyncio.sleep(0.2)
    _LOGGER.debug("All sensors have been restored properly")

    # we declare update_interval after initialization to avoid a first refresh before we setup entities
    rte_coordinator.update_interval = timedelta(minutes=16)
    enedis_coordinator.update_interval = timedelta(hours=1)
    if entry.data[CONF_ENEDIS_LOAD_SHEDDING][0]:
        # force a first refresh immediately to avoid waiting for 1 hour
        await enedis_coordinator.async_config_entry_first_refresh()
        enedis_coordinator._schedule_refresh()
    # force a first refresh immediately to avoid waiting for 16 minutes
    if any(
        s.state is None for s in sensors if s.coordinator == rte_coordinator
    ):  # one sensor needs immediate refresh
        await rte_coordinator.async_config_entry_first_refresh()
    else:
        # it means we might not get up to date info if HA was stopped for a while. TODO: detect last refresh for each sensor to take the best decision
        _LOGGER.info(
            "All sensors have already a known state, we'll wait next refresh to avoid hitting API limit after a restart"
        )
        rte_coordinator._schedule_refresh()
    _LOGGER.info("We finished the setup of ecowatt *entity*")
