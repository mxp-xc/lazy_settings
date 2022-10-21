# -*- coding: utf-8 -*-
from lazy_settings import SimpleLazySetting

DEBUG = False
PROJECT_NAME = "LAZY_SETTINGS"

PJN = SimpleLazySetting(key="data", ref="PROJECT_NAME")
