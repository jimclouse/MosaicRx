import tornado.ioloop
import tornado.web
import os
from tornado import ioloop
import httplib

class mainHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("index.html")

if __name__ == "__main__":
    # start up the servicef
    
    application = tornado.web.Application([
        (r"/",mainHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "website/")},),
        ],)

    try:
        application.listen(80)
        tornado.ioloop.IOLoop.instance().start()
        
    except Exception as e:
        raise e