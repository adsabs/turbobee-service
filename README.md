[![Build Status](https://travis-ci.org/adsabs/adsabs-webservices-blueprint.svg?branch=master)](https://travis-ci.org/adsabs/adsabs-webservices-blueprint)

# adsabs-webservices-blueprint

A sample Flask application for backend adsabs (micro) web services.

When starting a new microservice, do:

    * clone this repo
    * replace all occurrences of 'sample_application' with 'your_name'
    * rename 'sample application' to 'your_name' 
    * git commit/push

To integrate into the ADS-API, an application must expose a `/resources` route that advertises that application's resources, scopes, and rate limits. 

`GET` on `/resources` should return `JSON` that looks like:

    {
        "/route": {
            "scopes": ["red","green"],
            "rate_limit": [1000,86400],
            "description": "docstring for this route",
            "methods": ["HEAD","OPTIONS","GET"],
        }
    }


To facilitate that, one can define that route explitictly/manually or by using [flask-discoverer](https://github.com/adsabs/flask-discoverer). This blueprint is pre-configured to do just this.

## development

  * virtualenv virtualenv
  * source virtualenv/bin/activate
  * pip install -r dev-requirements.txt
  * pip install -r requirements.txt
  * python cors.py

Note: cors.py will start the microservice in a simple HTTP webserver with approparite CORS headers (so that you can access localhost:5000/.... from a browser). Normally, you would run
`python wsgi.py` or use a faster `gunicorn` to start `wsgi.py`.

## database migrations

DB schema is defined by migrations (inside alembic) folder, use these operations:

    * alembic upgrade head
    * alembic downgrade base
    * 