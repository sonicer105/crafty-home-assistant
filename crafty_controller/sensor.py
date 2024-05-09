import logging
import aiohttp
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Crafty Controller sensors, including regular and specific sensors."""
    crafty_base_url = config.get("crafty_base_url", "https://localhost:8000")
    api_token = config.get("api_token")
    verify_ssl = config.get("verify_ssl", True)

    if not api_token:
        LOGGER.error("No API token found for Crafty Controller integration.")
        return

    session = async_get_clientsession(hass)
    servers = await get_crafty_servers(crafty_base_url, api_token, verify_ssl, session)

    if servers:
        entities = []
        for server in servers:
            entities.append(CraftyServerSensor(server, crafty_base_url, api_token, verify_ssl, session))
            entities.append(CraftyMemorySensor(server, crafty_base_url, api_token, verify_ssl, session))
            entities.append(CraftyCpuSensor(server, crafty_base_url, api_token, verify_ssl, session))
        async_add_entities(entities, True)
    else:
        LOGGER.error("No servers found in Crafty Controller API.")


async def get_crafty_servers(base_url, api_token, verify_ssl, session):
    """Fetch the list of servers from the Crafty Controller API asynchronously."""
    headers = {"Authorization": f"Bearer {api_token}"}
    normalized_base_url = base_url.rstrip("/")

    try:
        async with session.get(f"{normalized_base_url}/api/v2/servers/", headers=headers, ssl=verify_ssl) as response:
            response.raise_for_status()
            response_json = await response.json()
            LOGGER.debug(f"Raw API response: {response_json}")
            return response_json.get("data", [])
    except (aiohttp.ClientError, ValueError) as err:
        LOGGER.error(f"Error fetching data from Crafty Controller API: {err}")
        return []


class CraftyServerSensor(SensorEntity):
    """General status sensor for a Crafty Controller server."""

    def __init__(self, server_data, base_url, api_token, verify_ssl, session):
        """Initialize the general server status sensor."""
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._verify_ssl = verify_ssl
        self._session = session
        self._server_id = server_data.get("server_id", "unknown")
        server_name = server_data.get("server_name", "unknown")
        self._name = f"Crafty {server_name} Status"
        self._state = None
        self._attributes = {
            "created": server_data.get("created", "unknown"),
            "server_id": self._server_id,
            "server_name": server_name,
            "auto_start": server_data.get("auto_start", "unknown"),
            "crash_detection": server_data.get("crash_detection", "unknown"),
            "server_ip": server_data.get("server_ip", "unknown"),
            "server_port": server_data.get("server_port", "unknown"),
            "type": server_data.get("type", "unknown")
        }

    @property
    def unique_id(self):
        """Return a unique ID prefixed with 'crafty'."""
        return f"crafty_{self._server_id}_status"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor (running or stopped)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return any additional state attributes."""
        return self._attributes

    async def async_update(self):
        """Fetch the latest server status data from the Crafty Controller API."""
        headers = {"Authorization": f"Bearer {self._api_token}"}
        try:
            async with self._session.get(
                f"{self._base_url}/api/v2/servers/{self._server_id}/stats",
                headers=headers, ssl=self._verify_ssl
            ) as response:
                response.raise_for_status()
                stats_data = await response.json()
                if stats_data["status"] == "ok":
                    server_stats = stats_data["data"]
                    self._state = "running" if server_stats.get("running", False) else "stopped"
                    self._attributes.update({
                        "started": server_stats.get("started", "unknown"),
                        "cpu": server_stats.get("cpu", "unknown"),
                        "mem": server_stats.get("mem", "unknown"),
                        "mem_percent": server_stats.get("mem_percent", "unknown"),
                        "world_size": server_stats.get("world_size", "unknown"),
                        "int_ping_results": server_stats.get("int_ping_results", "unknown"),
                        "max_players": server_stats.get("max", "unknown"),
                        "online_players": server_stats.get("online", "unknown"),
                        "desc": server_stats.get("desc", "unknown"),
                        "version": server_stats.get("version", "unknown"),
                        "updating": server_stats.get("updating", "unknown"),
                        "waiting_start": server_stats.get("waiting_start", "unknown"),
                        "first_run": server_stats.get("first_run", "unknown"),
                        "crashed": server_stats.get("crashed", "unknown"),
                        "downloading": server_stats.get("downloading", "unknown"),
                    })
                else:
                    LOGGER.error(f"Error in server stats response: {stats_data}")
        except (aiohttp.ClientError, ValueError) as err:
            LOGGER.error(f"Error updating Crafty Controller server status for {self._server_id}: {err}")


class CraftyMemorySensor(SensorEntity):
    """Memory usage sensor for a Crafty Controller server."""

    def __init__(self, server_data, base_url, api_token, verify_ssl, session):
        """Initialize the memory sensor."""
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._verify_ssl = verify_ssl
        self._session = session
        self._server_id = server_data.get("server_id", "unknown")
        server_name = server_data.get("server_name", "unknown")
        self._name = f"Crafty {server_name} Memory"
        self._state = None

    @property
    def unique_id(self):
        """Return a unique ID prefixed with 'crafty'."""
        return f"crafty_{self._server_id}_memory"

    @property
    def name(self):
        """Return the name of the sensor (including 'crafty')."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor (formatted in gigabytes)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return any additional state attributes."""
        return {"server_id": self._server_id}

    async def async_update(self):
        """Fetch the latest memory usage data from the server stats API."""
        headers = {"Authorization": f"Bearer {self._api_token}"}
        try:
            async with self._session.get(
                f"{self._base_url}/api/v2/servers/{self._server_id}/stats",
                headers=headers, ssl=self._verify_ssl
            ) as response:
                response.raise_for_status()
                stats_data = await response.json()
                if stats_data["status"] == "ok":
                    server_stats = stats_data["data"]
                    memory_value = server_stats.get("mem", 0)

                    if isinstance(memory_value, str):
                        if "GB" in memory_value:
                            self._state = f"{float(memory_value.replace('GB', '')):.3g}"
                        elif "MB" in memory_value:
                            self._state = f"{float(memory_value.replace('MB', '')) / 1024:.3g}"
                        else:
                            LOGGER.warning(f"Unexpected memory string format: {memory_value}")
                            self._state = "0"
                    elif isinstance(memory_value, (int, float)) and memory_value == 0:
                        self._state = "0"
                    else:
                        LOGGER.warning(f"Unexpected data type for memory: {type(memory_value)}")
                        self._state = "0"
        except (aiohttp.ClientError, ValueError) as err:
            LOGGER.error(f"Error updating memory stats for {self._server_id}: {err}")
            self._state = "0"


class CraftyCpuSensor(SensorEntity):
    """CPU usage sensor for a Crafty Controller server."""

    def __init__(self, server_data, base_url, api_token, verify_ssl, session):
        """Initialize the CPU sensor."""
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._verify_ssl = verify_ssl
        self._session = session
        self._server_id = server_data.get("server_id", "unknown")
        server_name = server_data.get("server_name", "unknown")
        self._name = f"Crafty {server_name} CPU"
        self._state = None

    @property
    def unique_id(self):
        """Return a unique ID prefixed with 'crafty'."""
        return f"crafty_{self._server_id}_cpu"

    @property
    def name(self):
        """Return the name of the sensor (including 'crafty')."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor (percentage)."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return any additional state attributes."""
        return {"server_id": self._server_id}

    async def async_update(self):
        """Fetch the latest CPU usage data from the server stats API."""
        headers = {"Authorization": f"Bearer {self._api_token}"}
        try:
            async with self._session.get(
                f"{self._base_url}/api/v2/servers/{self._server_id}/stats",
                headers=headers, ssl=self._verify_ssl
            ) as response:
                response.raise_for_status()
                stats_data = await response.json()
                if stats_data["status"] == "ok":
                    server_stats = stats_data["data"]
                    self._state = server_stats.get("cpu", "unknown")
        except (aiohttp.ClientError, ValueError) as err:
            LOGGER.error(f"Error updating CPU stats for {self._server_id}: {err}")
            self._state = "unknown"
