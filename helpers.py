from flask import redirect, render_template, request, session
from functools import wraps



# the following code is copied from CS50 2021 pset9 "finance"
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function