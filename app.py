import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'simulation'))

import tornado.ioloop
import tornado.web

# import simulatorLib
# import json

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
