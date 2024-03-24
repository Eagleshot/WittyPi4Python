## WittyPi4Python
### Overview
This Python module provides a convenient python interface for interacting with the [Witty Pi 4](https://www.uugear.com/product/witty-pi-4/) and [Witty Pi 4 Mini](https://www.uugear.com/product/witty-pi-4-mini/), a versatile power management and scheduling board for Raspberry Pi. 

### Features
- **Scheduling**: Create and apply customized schedule scripts.
- **Configuration**: Configure different parameters like the low and recovery voltage or synchronize the time with the internet.
- **Sensor Reading**: Read sensor values such as voltage, current and temperature from the Witty Pi 4 onboard sensors.

### Installation
Download the script to your Raspberry Pi the following command:
```bash
wget -O /home/pi/witty_pi_4.py https://raw.githubusercontent.com/Eagleshot/WittyPi4Python/main/witty_pi_4.py
```

### Example
```python
from witty_pi_4_module import WittyPi4

witty_pi_4 = WittyPi4()
witty_pi_4.sync_time_with_network()
temperature = witty_pi_4.get_temperature()
battery_voltage = witty_pi_4.get_battery_voltage()
internal_voltage = witty_pi_4.get_internal_voltage()
low_voltage_threshold = witty_pi_4.get_low_voltage_threshold()
witty_pi_4.set_low_voltage_threshold(3.5)
witty_pi_4.generate_schedule(8, 0, 30, 8)
next_startup_time = witty_pi_4.apply_schedule()
```

### Logging
The module uses the Python `logging` library to provide detailed log messages. You can configure the log level according to your needs.