#! /bin/sh
export FLASK_DEBUG=1
export FLASK_APP='ui/server/App.py'
export STATIC_JS='true'
flask run
# python ui/server/App.py
