#! python
import tornado.web
import traceback
import logging

logger = logging.getLogger('Mosaic')

class BaseHandler(tornado.web.RequestHandler):
    def _handle_request_exception(self, e):
        error = traceback.format_exc()
        logger.error(error)