from functools import wraps
from flask import Flask, make_response

def headers(headerDict={}, **headerskwargs):
    """This decorator adds the headers passed in to the response"""
    _headerDict = headerDict.copy()
    _headerDict.update(headerskwargs)
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in _headerDict.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


