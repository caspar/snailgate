#! /bin/sh
export FLASK_DEBUG=1
export FLASK_APP='ui/server/App.py'
python -m flask run
