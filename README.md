# seastar

[![PyPI - Version](https://img.shields.io/pypi/v/seastar.svg)](https://pypi.org/project/seastar)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/seastar.svg)](https://pypi.org/project/seastar)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install seastar
```

## Example
```
from seastar import web_function
from seastar.requests import Request
from seastar.respones import PlainTextResponse, Response


@web_function(methods=["POST"])
def app(request: Request) -> Response:
    return PlainTextResponse("Hello World!")

```

## License

`seastar` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
