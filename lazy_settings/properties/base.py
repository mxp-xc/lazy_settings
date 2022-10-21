# -*- coding: utf-8 -*-
import asyncio
from typing import Optional, Any, TYPE_CHECKING

from lazy_settings.exceptions import SettingLoadFail, ImproperlyConfigured

if TYPE_CHECKING:
    from lazy_settings.settings import Settings
    from lazy_settings.manager import BaseSettingManager


class BaseLazySetting(object):
    name: str
    _empty = object()

    def __init__(
            self,
            key: Optional[str] = None,
            ref: Optional[str] = None,
            default: Any = _empty
    ):
        self.key = key
        self.ref = ref
        self.default = default

    def set_name(self, name: str):
        self.name = name

    async def load(self, settings: "Settings", manager: "BaseSettingManager"):
        if self.key is not None:
            val = manager.data.get(self.key, self._empty)
            if val is not self._empty:
                setattr(settings, self.name, val)
                return

        if self.ref is not None:
            val = getattr(settings, self.ref, self._empty)
            if val is not self._empty and not isinstance(val, BaseLazySetting):
                setattr(settings, self.name, val)
                return

        if self.default is not self._empty:
            if callable(self.default):
                if asyncio.iscoroutinefunction(self.default):
                    default = await self.default()
                else:
                    default = self.default()
                setattr(settings, self.name, default)
            else:
                setattr(settings, self.name, self.default)

        raise SettingLoadFail

    def __get__(self, instance, owner):
        raise ImproperlyConfigured(f"`{self.name}` not config yet")
