from dataclasses import asdict, is_dataclass
from datetime import datetime, date, time
from enum import Enum
import inspect
from json import JSONEncoder
from typing import Any
from uuid import UUID


class JsonEncoder(JSONEncoder):

    def default(self, o: Any) -> Any:
        if not inspect.isclass(o) and is_dataclass(o):
            return asdict(o)

        elif isinstance(o, (datetime, date, time)):
            return o.isoformat()

        elif isinstance(o, Enum):
            return o.value

        elif isinstance(o, UUID):
            return str(o)
