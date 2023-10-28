# SPDX-FileCopyrightText: 2023-present Ryan Kroon <rykroon.tech@gmail.com>
#
# SPDX-License-Identifier: MIT
__version__ = "0.4.0"


"""
Ideas

- Differentiate between a WebRoute and an EventRoute
    - matches() raises NotImplementedError on BaseRoute

- Exception Middleware can accept a is_web flag.
    - This will allow the exception middleware to be used for non-web events.


"""
