# SPDX-License-Identifier: GPL-3.0-or-later
"""Small v2 API adapter for the converter's models, using pure-Python Pydantic v1.

Android has no supported v2 Rust wheel. Keep v1's validation and recursive
model conversion; add only the APIs used by ebtools. Pack hashes remain the
final authority, so a compatibility difference cannot install different data.
"""
import json
from typing import ClassVar, get_origin
try:
    from pydantic.v1 import BaseModel as V1Model, Field, ValidationError
    from pydantic.v1.main import ModelMetaclass
    from pydantic.v1.fields import FieldInfo
    from pydantic.v1.json import pydantic_encoder
except ImportError:
    from pydantic import BaseModel as V1Model, Field, ValidationError
    from pydantic.main import ModelMetaclass
    from pydantic.fields import FieldInfo
    from pydantic.json import pydantic_encoder

ConfigDict = dict

def computed_field(value):
    value.fget.__android_computed__ = True
    return value

class ConverterMetaclass(ModelMetaclass):
    def __new__(mcls, name, bases, namespace, **kwargs):
        for key, annotation in namespace.get('__annotations__', {}).items():
            field = namespace.get(key)
            if get_origin(annotation) in (list, tuple) and isinstance(field, FieldInfo):
                field.min_items, field.max_items = field.min_length, field.max_length
                field.min_length = field.max_length = None
        config = namespace.get('model_config', {})
        if config:
            namespace['Config'] = type('Config', (), {'extra': config.get('extra', 'ignore'),
                                                       'allow_mutation': not config.get('frozen', False)})
        return super().__new__(mcls, name, bases, namespace, **kwargs)

class BaseModel(V1Model, metaclass=ConverterMetaclass):
    model_config: ClassVar[dict] = {}

    @classmethod
    def model_validate(cls, value):
        return cls.parse_obj(value)

    @classmethod
    def model_validate_json(cls, value):
        return cls.parse_raw(value)

    def _iter(self, *args, **kwargs):
        yield from super()._iter(*args, **kwargs)
        if kwargs.get('to_dict'):
            for cls in reversed(type(self).__mro__):
                for name, prop in vars(cls).items():
                    if isinstance(prop, property) and getattr(prop.fget, '__android_computed__', False):
                        yield name, getattr(self, name)

    def model_dump(self, **kwargs):
        kwargs.pop('mode', None)
        return self.dict(**kwargs)

    def model_dump_json(self, **kwargs):
        indent = kwargs.pop('indent', None)
        return json.dumps(self.model_dump(**kwargs), default=pydantic_encoder,
                          ensure_ascii=False, indent=indent)
