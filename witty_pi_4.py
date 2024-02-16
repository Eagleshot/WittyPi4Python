'''A python module for interacting with the Witty Pi 4 board'''
from subprocess import check_output, STDOUT
from os import path
import logging

WITTYPI_DIRECTORY = "/home/pi/wittypi"
SCHEDULE_FILE_PATH = f"{WITTYPI_DIRECTORY}/schedule.wpi"

class WittyPi4:
    '''A class for interacting with the Witty Pi 4 board'''
    def __init__(self):
        logging.info("Initializing Witty Pi 4 interface")

    # Get WittyPi readings
    # See: https://www.baeldung.com/linux/run-function-in-script
    def run_command(self, command: str) -> str:
        '''Run a Witty Pi 4 command'''
        try:
            command = f"cd {WITTYPI_DIRECTORY} && . ./utilities.sh && {command}"
            output = check_output(command, shell=True, executable="/bin/bash", stderr=STDOUT, universal_newlines=True, timeout=3)
            return output.strip()
        except Exception as e:
            logging.error("Could not run Witty Pi 4 command: %s", str(e))
            return "ERROR"

    def sync_time_with_network(self) -> None:
        '''Sync Witty Pi 4 clock with network time'''

        # See: https://www.uugear.com/forums/technial-support-discussion/witty-pi-4-how-to-synchronise-time-with-internet-on-boot/
        try:
            output = self.run_command("net_to_system && system_to_rtc")
            logging.info("Time synchronized with network: %s", output)
        except Exception as e:
            logging.error("Could not synchronize time with network: %s", str(e))

    def get_temperature(self) -> float:
        '''Gets the current temperature reading from the Witty Pi 4 in °C'''
        try:
            temperature = self.run_command("get_temperature")
            temperature = temperature.split("/", maxsplit = 1)[0] # Remove the Farenheit reading
            temperature = temperature[:-3] # Remove °C
            temperature = float(temperature)
            logging.info("Temperature: %s °C", temperature)
            return temperature
        except Exception as e:
            logging.error("Could not get temperature: %s", str(e))
            return -273.15

    def get_battery_voltage(self) -> float:
        '''Gets the battery voltage reading from the Witty Pi 4 in V'''
        try:
            battery_voltage = self.run_command("get_input_voltage")
            battery_voltage = float(battery_voltage) # Remove V
            logging.info("Battery voltage: %s V", battery_voltage)
            return battery_voltage
        except Exception as e:
            logging.error("Could not get battery voltage: %s", str(e))
            return 0.0

    def get_internal_voltage(self) -> float:
        '''Gets the internal (5V) voltage from the Witty Pi 4 in V'''
        try:
            internal_voltage = self.run_command("get_output_voltage")
            internal_voltage = float(internal_voltage)
            logging.info("Output voltage: %s V", internal_voltage)
            return internal_voltage
        except Exception as e:
            logging.error("Could not get Raspberry Pi voltage: %s", str(e))
            return 0.0

    def get_internal_current(self) -> float:
        '''Gets the internal (5V) current reading from the Witty Pi 4 in A'''
        try:
            internal_current = self.run_command("get_output_current")
            internal_current = float(internal_current)
            logging.info("Output current: %s A", internal_current)
            return internal_current
        except Exception as e:
            logging.error("Could not get Raspberry Pi current: %s", str(e))
            return 0.0

    def get_low_voltage_threshold(self) -> float:
        '''Gets the low threshold from the Witty Pi 4'''
        try:
            low_voltage_threshold = self.run_command("get_low_voltage_threshold")

            if low_voltage_threshold == "disabled":
                logging.info("Low voltage threshold: disabled")
                return 0.0

            low_voltage_threshold = float(low_voltage_threshold[:-1])
            logging.info("Low voltage threshold: %s V", low_voltage_threshold)
            return low_voltage_threshold

        except Exception as e:
            logging.error("Could not get low voltage threshold: %s", str(e))
            return 0.0

    def get_recovery_voltage_threshold(self) -> float:
        '''Gets the recovery threshold from the Witty Pi 4'''
        try:
            recovery_voltage_threshold = self.run_command("get_recovery_voltage_threshold")

            if recovery_voltage_threshold == "disabled":
                logging.info("Recovery voltage threshold: disabled")
                return 0.0

            recovery_voltage_threshold = float(recovery_voltage_threshold[:-1])
            logging.info("Recovery voltage threshold: %s V", recovery_voltage_threshold)
            return recovery_voltage_threshold

        except Exception as e:
            logging.error("Could not get recovery voltage threshold: %s", str(e))
            return 0.0

    def set_low_voltage_threshold(self, voltage: float) -> float:
        '''Sets the low voltage threshold from the Witty Pi 4'''
        try:
            if voltage != self.get_low_voltage_threshold():
                low_voltage_threshold = self.run_command(f"set_low_voltage_threshold {int(voltage*10)}")
                logging.info("Set low voltage threshold to: %s V", voltage)
                return low_voltage_threshold

            logging.info("Low voltage threshold already set to: %s V", voltage)
            return voltage

        except Exception as e:
            logging.error("Could not set low voltage threshold: %s", str(e))
            return 0.0

    # Set recovery voltage threshold
    def set_recovery_voltage_threshold(self, voltage: float) -> float:
        '''Sets the recovery voltage threshold from the Witty Pi 4'''
        try:
            if voltage != self.get_recovery_voltage_threshold():
                recovery_voltage_threshold = self.run_command(f"set_recovery_voltage_threshold {int(voltage*10)}")
                logging.info("Set recovery voltage threshold to: %s V", voltage)
                return recovery_voltage_threshold

            logging.info("Recovery voltage threshold already set to: %s V", voltage)
            return voltage

        except Exception as e:
            logging.error("Could not set recovery voltage threshold: %s", str(e))
            return 0.0

    @staticmethod
    def generate_schedule(start_hour: int, start_minute: int, interval_length_minutes: int, num_repetitions_per_day: int) -> None:
        '''Generate a startup schedule file for Witty Pi 4'''

        max_duration_minutes = 4

        # Basic validity check of parameters
        if not 0 < start_hour < 24:
            start_hour = 8

        if not 0 < start_minute < 60:
            start_minute = 0

        if not 0 < interval_length_minutes < 1440:
            interval_length_minutes = 30

        if not 0 < num_repetitions_per_day < 250:
            num_repetitions_per_day = 8

        if ((num_repetitions_per_day * interval_length_minutes) + start_minute + (start_hour * 60)) > 1440:
            num_repetitions_per_day = 1

        # 2037 is the maximum year for WittyPi
        formatted_start_time = f"{start_hour:02d}:{start_minute:02d}"
        schedule = f"BEGIN\t2020-01-01 {formatted_start_time}:00\nEND\t2037-12-31 23:59:59\n"

        for i in range(num_repetitions_per_day):
            schedule += f"ON\tM{max_duration_minutes}\n"

            # Last off is different
            if i < num_repetitions_per_day - 1:
                # Your code here
                schedule += f"OFF\tM{interval_length_minutes - max_duration_minutes}\n"

        # Turn camera off for the rest of the day
        remaining_minutes = 1440 - (num_repetitions_per_day * interval_length_minutes) + (interval_length_minutes - max_duration_minutes)
        remaining_hours = remaining_minutes // 60
        remaining_minutes = remaining_minutes % 60

        schedule += f"OFF\tH{remaining_hours}"
        if remaining_minutes > 0:
            schedule += f" M{remaining_minutes}"

        if path.exists(SCHEDULE_FILE_PATH):
            with open(SCHEDULE_FILE_PATH, "r", encoding='utf-8') as f:
                old_schedule = f.read()

                # Write new schedule file if it changed
                if old_schedule != schedule:
                    logging.info("Schedule changed - writing new schedule file.")
                    with open(SCHEDULE_FILE_PATH, "w", encoding='utf-8') as f:
                        f.write(schedule)
                else:
                    logging.info("Schedule did not change.")
        else:
            logging.warning("Schedule file not found. Writing new schedule file.")
            with open(SCHEDULE_FILE_PATH, "w", encoding='utf-8') as f:
                f.write(schedule)

    def apply_schedule(self, max_retries: int = 5) -> str:
        '''Apply schedule to Witty Pi 4'''
        for _ in range(max_retries):
            try:
                # Apply new schedule
                command = f"cd {WITTYPI_DIRECTORY} && sudo ./runScript.sh"
                output = check_output(command, shell=True, executable="/bin/bash", stderr=STDOUT, universal_newlines=True, timeout=10)
                output = output.split("\n")[1:3]

                if "Schedule next startup at:" in output[1]:
                    logging.info("%s", output[0])
                    logging.info("%s", output[1])
                    next_startup_time = output[1][-19:]
                    return next_startup_time

                logging.warning("Failed to apply schedule: %s", output[0])
                self.sync_time_with_network()
 
            except Exception as e:
                logging.error("Failed to apply schedule: %s", str(e))
                return "-"

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    witty_pi_4 = WittyPi4()
    witty_pi_4.sync_time_with_network()
    witty_pi_4.get_temperature()
    witty_pi_4.get_battery_voltage()
    witty_pi_4.get_internal_voltage()
    witty_pi_4.get_internal_current()
    witty_pi_4.get_low_voltage_threshold()
    witty_pi_4.get_recovery_voltage_threshold()
    witty_pi_4.set_low_voltage_threshold(3.5)
    witty_pi_4.set_recovery_voltage_threshold(3.7)
    witty_pi_4.generate_schedule(8, 0, 30, 8)
    witty_pi_4.apply_schedule()
