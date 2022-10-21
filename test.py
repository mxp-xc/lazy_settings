# -*- coding: utf-8 -*-

import os

from lazy_settings.const import LAZY_SETTINGS_MODULE
from lazy_settings import settings, SimpleSettingManager

os.environ[LAZY_SETTINGS_MODULE] = "settings"


async def main():
    await asyncio.sleep(4)
    print(settings.PJN)


@SimpleSettingManager.loader
async def loader():
    await asyncio.sleep(3)
    return {"data": 123}


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
