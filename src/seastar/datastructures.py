from collections.abc import Mapping
from typing import Optional
from starlette import datastructures


class FormData(datastructures.ImmutableMultiDict):
    pass


class Headers(datastructures.Headers):
    
    def __init__(
        self,
        headers: Optional[Mapping[str, str]] = None,
        raw: Optional[list[tuple[bytes, bytes]]] = None,
    ) -> None:
        """
            Removed 'scopes' parameter.
        """
        super().__init__(headers=headers, raw=raw, scope=None)


class MutableHeaders(Headers, datastructures.MutableHeaders):
    pass
