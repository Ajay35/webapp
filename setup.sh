#!/bin/bash

export FLASK_APP=flaskr
export FLASK_ENV=development
#flask init-db

sudo -i service elasticsearch start
flask run
