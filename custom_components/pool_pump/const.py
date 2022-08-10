"""Constants for blueprint."""
# Base component constants
NAME = "Pool Pump Manager"
DOMAIN = "pool_pump"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.2beta1"

ISSUE_URL = "https://github.com/oncleben31/ha-pool_pump/issues"
DOC_URL = "https://github.com/oncleben31/ha-pool_pump"

# Icons
ICON = "mdi:format-quote-close"

# Common constants
POOL_PUMP_MODE_AUTO = "Auto"
ATTR_POOL_PUMP_MODE_ENTITY_ID = "pool_pump_mode_entity_id"
ATTR_WATER_LEVEL_CRITICAL_ENTITY_ID = "water_level_critical_entity_id"

ATTR_SWITCH_ENTITY_ID = "switch_entity_id"

# Constants for @oncleben31 mode
ATTR_POOL_TEMPERATURE_ENTITY_ID = "pool_temperature_entity_id"
ATTR_TOTAL_DAILY_FILTERING_DURATION = "total_daily_filtering_duration"
ATTR_NEXT_RUN_SCHEDULE = "next_run_schedule"
ATTR_SCHEDULE_BREAK_DURATION_IN_HOURS = "schedule_break_in_hours"
DEFAULT_BREAK_DURATION_IN_HOURS = 0.0

# Constants for @exxamalte mode
# Removed

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
