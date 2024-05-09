# Crafty Controller Integration for Home Assistant

This is a custom integration for [Home Assistant](https://www.home-assistant.io/) that allows you to monitor Minecraft servers managed by [Crafty Controller](https://craftycontrol.com/). It provides sensors for tracking general server status, CPU usage, memory usage, and other metrics.

It's worth noting that Python is not a language I have a lot of experience with. This can probably be written a lot better and a lot cleaner. You are welcome to try and improve it.

This was last verified working against Home Assistant 2024.5.2 and Crafty Controller 4.3.2

## Features

- **General Status:** Monitor server uptime status (running or stopped).
- **CPU Usage:** Track server CPU usage in percentage.
- **Memory Usage:** Track server memory usage in gigabytes.
- **Additional Attributes:** View player count, server ports, and more.

## Installation

1. **Download the Custom Component:**
   - Clone this repository or download it as a zip file.

2. **Copy to `custom_components`:**
   - Copy the `crafty_controller` folder into your Home Assistant `custom_components` directory. This is located in the config folder. Create it if it's not present.

3. **Update `configuration.yaml`:**
   - Add the following configuration to your `configuration.yaml` file:
   ```YAML
   sensor:
     - platform: crafty_controller
       crafty_base_url: "https://your-crafty-server-url:8443"
       api_token: "YOUR_API_TOKEN"
       verify_ssl: true # or false to disable SSL verification
   ```

4. **Restart Home Assistant:**
   - Restart your Home Assistant instance to load the custom component.

## Development Setup

To set up a development environment, follow these steps:

1. **Create a Virtual Environment:**
   - Create a virtual environment for Home Assistant:
   ```
   python3 -m venv venv
   ```

2. **Activate the Virtual Environment:**
   - On Windows:
   ```
   venv\Scripts\activate
   ```
   - On Linux/macOS:
   ```
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   - Install `homeassistant-stubs` and other development dependencies:
   ```
   pip install -r dev-requirements.txt
   ```

4. **Linting and Typing:**
   - Optionally, use linting tools like `flake8` and type-checkers like `mypy` for code quality:
   ```
   flake8 crafty_controller
   mypy crafty_controller
   ```

5. **Run Home Assistant in Development Mode:**
   - Start Home Assistant with the `--debug` flag:
   ```
   hass --debug
   ```

## Usage

After installation and configuration, the integration will automatically create the following sensors:

1. **General Status Sensor:** Reports whether the server is running or stopped.
2. **CPU Usage Sensor:** Shows server CPU usage as a percentage.
3. **Memory Usage Sensor:** Displays memory usage in gigabytes.

These sensors can be used in Home Assistant automations, dashboards, and scripts.

## Troubleshooting

- Ensure that the Crafty Controller API is accessible and that the provided API token has sufficient permissions.
- Check the Home Assistant logs for error messages related to `crafty_controller`.

## Contributions

Contributions are welcome! Feel free to open issues or submit pull requests to improve the integration.

## Acknowledgements

This project was built with the assistance of ChatGPT for code suggestions and documentation.

## License

This project is licensed under the MIT License.
