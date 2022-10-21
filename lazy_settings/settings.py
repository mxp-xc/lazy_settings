# -*- coding: utf-8 -*-
import asyncio
import os
import importlib
from typing import List, Sequence

from lazy_settings.exceptions import ImproperlyConfigured
from lazy_settings.manager import BaseSettingManager
from lazy_settings.const import LAZY_SETTINGS_MODULE, LAZY_SETTINGS_MANAGERS

from django.conf import LazySettings as _LazySettings
from django.utils.module_loading import import_string

DEFAULT_SETTINGS_MANAGERS = [
    "lazy_settings.manager.SimpleSettingManager"
]


class Settings:
    _managers: List[BaseSettingManager]

    def __init__(self, settings_module):
        self.SETTINGS_MODULE = settings_module
        self._managers = []

        mod = importlib.import_module(settings_module)
        manager_paths = getattr(mod, LAZY_SETTINGS_MANAGERS, DEFAULT_SETTINGS_MANAGERS)
        self._load_managers(manager_paths)

        self._explicit_settings = set()
        for setting in dir(mod):
            if not setting.isupper():
                continue
            setting_value = getattr(mod, setting)
            for manager in self._managers:
                if isinstance(setting_value, manager.setting_class):
                    manager.add_setting(setting, setting_value)
                    break
            else:
                setattr(self, setting, setting_value)

            self._explicit_settings.add(setting)

        asyncio.get_running_loop().create_task(self._configure_lazy_async())

    def is_overridden(self, setting):
        return setting in self._explicit_settings

    def _load_managers(self, manager_paths: Sequence[str]):
        for path in manager_paths:
            manager_class = import_string(path)
            self._managers.append(manager_class(self))

    async def _configure_lazy_async(self):
        await asyncio.gather(*(
            manager.configure()
            for manager in self._managers
        ))

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            "cls": self.__class__.__name__,
            "settings_module": self.SETTINGS_MODULE,
        }

    async def wait(self):
        for manager in self._managers:
            await manager.wait()


class LazySettings(_LazySettings):
    def _setup(self, name=None):
        settings_module = os.environ.get(LAZY_SETTINGS_MODULE)
        if not settings_module:
            desc = ("setting %s" % name) if name else "settings"
            raise ImproperlyConfigured(
                "Requested %s, but settings are not configured. "
                "You must either define the environment variable %s "
                "or call settings.configure() before accessing settings."
                % (desc, LAZY_SETTINGS_MODULE)
            )

        self._wrapped = Settings(settings_module)


settings = LazySettings()
