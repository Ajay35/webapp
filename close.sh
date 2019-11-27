#!/bin/bash

rm -rf flaskr/__pycache__
rm instance/flaskr.sqlite
sudo -i service elasticsearch stop
