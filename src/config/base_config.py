from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    check_battery_interval: int = 15

    @property
    def battery_interval(self) -> int:
        return self.check_battery_interval

    @battery_interval.setter
    def battery_interval(self, interval: int):
        self.check_battery_interval = interval


base_settings = BaseConfig()
