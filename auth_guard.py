# -*- coding: utf-8 -*-
"""
Auth guard surface for protected routes.

Route modules import the dependency from here and attach it with `Depends(...)`:

    from auth_guard import get_current_user

    @app.get("/analyze")
    def analyze(user: dict = Depends(get_current_user)):
        ...

`get_current_user` requires a valid Bearer access token and raises HTTP 401
otherwise. Validation is pure JWT verification (HS256) — no database round-trip —
so guarding an endpoint adds well under a millisecond and stays horizontally
scalable. `get_current_user_optional` returns None instead of raising, for
endpoints that adapt to an anonymous caller.

The implementations live in `auth.py`; this module is the stable import point so
handlers don't pull in the auth router / DB pool directly.
"""

from auth import get_current_user, get_current_user_optional

__all__ = ["get_current_user", "get_current_user_optional"]
