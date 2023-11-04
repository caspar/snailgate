#! /bin/sh
export FLASK_APP='ui/server/App.py'
export STATIC_JS='true'
flask run --host=0.0.0.0 --port=5001
