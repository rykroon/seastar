# SPDX-FileCopyrightText: 2023-present Ryan Kroon <rykroon.tech@gmail.com>
#
# SPDX-License-Identifier: MIT
__version__ = "0.3.0"


"""
    One of the more difficult things of designing this API is the naming convention.
    
    In the documentation they refer to the "main" function as the "entry point" or "handler."

    This has me thinking I should go back to referring to these functions as "handlers".
    And then perhaps I can refer to the top-level handler as the "entry point".


    I am currently drunk and considering an idea that would basically make most of my
    work useless...
    WHAT IF! 
    instead of rewriting a starlette like framework.

    what If I just created an interface that converted Digital Ocean's event and context
    into a an ASGI scope, receive, send. 


"""