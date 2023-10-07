from dataclasses import asdict, is_dataclass
from datetime import datetime, date, time
from enum import Enum
from json import JSONEncoder
from uuid import UUID


class JsonEncoder(JSONEncoder):

    def default(self, o):
        if is_dataclass(o):
            return asdict(o)

        elif isinstance(o, (datetime, date, time)):
            return o.isoformat()

        elif isinstance(o, Enum):
            return o.value

        elif isinstance(o, UUID):
            return str(o)

        return super().default(o)
