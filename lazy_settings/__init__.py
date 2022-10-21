# -*- coding: utf-8 -*-
import typing as _t

from lazy_settings.settings import settings

from lazy_settings.properties.simple import SimpleLazySetting
from lazy_settings.manager import SimpleSettingManager


if _t.TYPE_CHECKING:
    from django.conf import settings  # noqa
