"""Skip support queries entirely when no held geometry exists."""
from __future__ import annotations
import importlib.util
from pathlib import Path

FEATURES=('reentry16_active','reentry32_active')

def apply(source,feature):
    if feature not in FEATURES:raise ValueError(feature)
    path=Path(__file__).with_name('patch_reentry.py')
    spec=importlib.util.spec_from_file_location('frozen_reentry_policy',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.apply(source,feature.removesuffix('_active'))
    old='const bool reentry_danger_recent = P_HOLD && P_DANGER &&'
    new='const bool reentry_danger_recent = P_HOLD && s.hold >= 0 && P_DANGER &&'
    if result['main.cpp'].count(old)!=1:raise ValueError('Re-entry activity anchor changed')
    result['main.cpp']=result['main.cpp'].replace(old,new,1)
    return result
