# -*- coding: utf-8 -*-
import asyncio
from typing import Dict, TYPE_CHECKING, Type
from types import MappingProxyType

from lazy_settings.exceptions import ImproperlyConfigured, SettingLoadFail
from lazy_settings.properties.base import BaseLazySetting
from lazy_settings.properties.simple import SimpleLazySetting

from django.utils.functional import cached_property, classproperty

if TYPE_CHECKING:
    from .settings import Settings


class BaseSettingManager(object):
    setting_class: Type[BaseLazySetting]

    def __init__(self, settings: "Settings"):
        self.settings = settings
        self._event = asyncio.Event()
        self._settings: Dict[str, BaseLazySetting] = {}
        self._configured = False
        self._data = {}

    def add_setting(self, name: str, setting: BaseLazySetting):
        if name in self._settings:
            raise ImproperlyConfigured(f"重复的配置名: {name}")
        setattr(self.settings.__class__, name, setting)
        setting.set_name(name)
        self._settings[name] = setting

    async def configure(self):
        if self._configured:
            return

        self._data = await self.load_data()
        lazy_settings = set(self._settings.values())

        while len(lazy_settings):
            count = len(lazy_settings)
            for setting in tuple(lazy_settings):
                try:
                    await setting.load(self.settings, self)
                except SettingLoadFail:
                    continue
                lazy_settings.discard(setting)

            if len(lazy_settings) == count:
                keys = [setting.name for setting in lazy_settings if setting.key is not None]
                refs = [setting.name for setting in lazy_settings if setting.ref is not None]
                msg = [""]
                if keys:
                    msg.append(f"\t不存在的keys: {keys}")
                if refs:
                    msg.append(f"\t\t循环引用: {refs}")
                raise ImproperlyConfigured("\n".join(msg))
        self._configured = True
        self._event.set()

    async def load_data(self):  # noqa
        self._data = {}

    async def wait(self):
        await self._event.wait()

    @cached_property
    def data(self):
        return MappingProxyType(self._data)

    @classproperty
    def loader(cls):  # noqa
        def wrapper(func):
            if not asyncio.iscoroutinefunction(func):
                raise ImproperlyConfigured("need async loader")
            cls.load_data = lambda self: func()

        return wrapper

    @property
    def configured(self) -> bool:
        return self._configured


class SimpleSettingManager(BaseSettingManager):
    setting_class = SimpleLazySetting
