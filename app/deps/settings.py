from typing import Annotated

from fastapi import Depends

from app.config.settings import Settings


def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
