from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    check_battery_interval: int
    database_url: str

    @property
    def battery_interval(self) -> int:
        return self.check_battery_interval

    @battery_interval.setter
    def battery_interval(self, interval: int):
        self.check_battery_interval = interval

    class Config:
        env_file = "./.env"
        env_file_encoding = "utf-8"


base_settings = BaseConfig()
