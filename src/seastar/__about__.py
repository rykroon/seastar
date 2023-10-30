# SPDX-FileCopyrightText: 2023-present Ryan Kroon <rykroon.tech@gmail.com>
#
# SPDX-License-Identifier: MIT
__version__ = "0.4.0"


"""
Ideas

- Routes will almost always only make sense within the context of web events.
    - if a route or routes were to be used outside the context of a web event, it would
    essentially be any ambiguous conditional logic which could just be added by the developer in
    the function.

    So routes should always assume a function with the following signature:
        def func(request: Request) -> Response: ...
    
    however when it comes to exceptions, one might prefer the def exc_handler(event, context, exc) over
        def exc_handler(request, exc):

 - orrrrr Just add a decorator for transforming a request exception handler to an event exception handler.
 - use inspect.siganture to check if it has 2 or 3 parameters.
"""
