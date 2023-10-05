# Built-in
import os
import re
from logging import getLogger
from typing import List, Tuple, Union
import warnings
logger = getLogger(__name__)


class _FromDictMixin:
    """
    usage:
    class A(_FromDictMixin):
        field1 = None
        field2 = "default"
        field3 = "default3"
        fields_required = ["field1", ("field2", "field3)] # field 1 is required, and at least one of field2 or field3

        def from_dict_field1(self, value): # optional
           # make some check / transform the value
           self.field1 = value

        def to_dict_field1(self): # optional
            # return the representation of field1
            return value

        def validate(self, current_depth=""): # this is optional
            # place your code de validate all field
    """

    fields_required: List[Union[str, Tuple]] = []

    def __init__(self, **kwargs):
        super().__init__()
        self.from_dict(kwargs)

    def from_dict(self, d: dict, current_depth: str = "") -> None:
        """
        Load object from dict.
        Values can be a natif value, a environ "env(name)"
        """
        for k, v in d.items():
            if isinstance(v, str):
                pattern = r"env\((?P<var_name>[A-Z_]+)(\s*,\s*(?P<default>[\w.-]+))?\)"
                match = re.match(pattern, v)
                if match:
                    logger.debug(
                        "key %s is an env var. Getting it" % current_depth + "." + k
                    )
                    v = os.getenv(match.group("var_name"), match.group("default"))
            if hasattr(self, f"from_dict_{k}"):
                # has from_dict_XXX(), then call it
                func = getattr(self, f"from_dict_{k}")
                func(v)
            elif hasattr(self, f"set_{k}"):
                # has set_XXX(), then call it
                warnings.warn("set_XXX is deprecated. Please use from_dict_XXX instead", DeprecationWarning, stacklevel=2)
                func = getattr(self, f"set_{k}")
                func(v)
            elif hasattr(self, k):
                # has XXX, then set it
                attr = getattr(self, k)
                if isinstance(v, dict) and isinstance(attr, _FromDictMixin):
                    attr.from_dict(v, current_depth=current_depth + "." + k)
                else:
                    setattr(self, k, v)
        self.validate(current_depth=current_depth)

    def is_valid(self) -> bool:
        for field in self.fields_required:
            res = False
            if isinstance(field, str):
                field = [field]  # type: ignore
            for f in field:
                res |= bool(getattr(self, f, None))
            if not res:
                return False
        return True

    def validate(self, current_depth: str = "") -> None:
        errors = []
        for field in self.fields_required:
            res = False
            if isinstance(field, str):
                field = [field]  # type: ignore
            for f in field:
                res |= bool(getattr(self, f, None))
            if not res:
                errors.append(str(field))
        if errors:
            fields = ", ".join(errors)
            msg = f"In '{current_depth}' configuration, mandatory fields '{fields}' are missing"
            logger.error(msg)
            raise ValueError(msg)

    def to_dict(self):
        class_vars = vars(self.__class__)  # get any "default" attrs defined at the class level
        inst_vars = vars(self)  # get any attrs defined on the instance (self)
        all_vars = dict(class_vars)
        all_vars.update(inst_vars)

        result = {}
        for k, v in all_vars.items():
            # filter out private attributes and callable
            if k.startswith('_') or callable(getattr(self, k)):
                continue

            if hasattr(self, f"to_dict_{k}"):
                # has to_dict_XXX(), then call it
                func = getattr(self, f"to_dict_{k}")
                result[k] = func()
            elif isinstance(v, _FromDictMixin):
                result[k] = v.to_dict()
            # elif isinstance(v, (list, tuple)) and isinstance(v[0], _FromDictMixin):
            #     result[k] = [v2.to_dict() for v2 in v]
            else:
                result[k] = v
        return result

    def __repr__(self) -> str:
        return str(self.to_dict())
