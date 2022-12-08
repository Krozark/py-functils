# Built-in
import os
import re
from logging import getLogger
from typing import List, Tuple, Union

logger = getLogger(__name__)


class _FromDictMixin:
    """
    usage:
    class A(_FromDictMixin):
        field1 = None
        field2 = "default"
        field3 = "default3"
        fields_required = ["field1", ("field2", "field3)] # field 1 is required, and at least one of field2 or field3

        def set_field1(self, value): # optional
           # make some check
           self.field1 = value

        def validate(self, current_depth=""): # thi si is optional
            # place your code de validate all field
    """

    fields_required: List[Union[str, Tuple]] = []

    def from_dict(self, d: dict, current_depth: str = "") -> None:
        for k, v in d.items():
            if isinstance(v, str):
                pattern = r"env\((?P<var_name>[A-Z_]+)(\s*,\s*(?P<default>[\w.-]+))?\)"
                match = re.match(pattern, v)
                if match:
                    logger.debug(
                        "key %s is an env var. Getting it" % current_depth + "." + k
                    )
                    v = os.getenv(match.group("var_name"), match.group("default"))
            if hasattr(self, f"set_{k}"):
                # has set_XXX(), then call it
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

    def __repr__(self) -> str:
        return str(self.__dict__)
