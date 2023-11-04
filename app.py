import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'simulation'))

import json

import tornado.ioloop
import tornado.web

from simulation import simulatorLib


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
