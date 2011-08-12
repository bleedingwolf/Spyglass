# Spyglass

A simple webapp for logging and sharing HTTP requests.

## Installation

    git clone git://github.com/bleedingwolf/Spyglass.git
    cd Spyglass/spyglass_demo
    pip install -r pip-requirements.txt
    python manage.py syncdb --all

## Usage

Run both of the following from two separate consoles:
    
  * `python manage.py runserver`
  * `python manage.py celeryd`

If you have `foreman` installed, you can also run both at once with `foreman start`.

## Authors

Spyglass was implemented by Justin Voss, circa 2010.

This implementation is licensed under a permissive BSD-style license, with the exception of the included libraries, which are licensed as follows:

JQuery 1.4.2: MIT or GPL 2, at your option

less.js 1.0.30: Apache 2.0