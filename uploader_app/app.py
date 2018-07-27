import os
import logging
import falcon
from falcon_cors import CORS
from .env_config import Config

from .controllers.uploader import UploadController

# Middlewares
from falcon_multipart.middleware import MultipartMiddleware

def prepare_log(logs_path=Config.LOGS_PATH, log_file=Config.APP_LOG):
    """
    Prepare the logging for the Websockets Middleware
    """
    if not os.path.exists(logs_path):
        try:
            os.mkdir(logs_path)
        except:
            print("Couldn't create log path {}".format(logs_path))
    log_file = os.path.join(logs_path, log_file)
    logging.basicConfig(filename=log_file, format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

# Prepare the logger
prepare_log()

# CORS
logging.info("Starting the CORS connection for Falcon")
cors = CORS(allow_all_origins=True,
            allow_all_methods=True,
            allow_all_headers=True,
            allow_credentials_all_origins=True)

# Init falcon API
app = application = falcon.API(middleware=[cors.middleware, MultipartMiddleware()])
logging.info("Setting middlewares: cors.middleware, MultipartMiddleware()")


# API routes definitions
app.add_static_route('/' + Config.DATA_FILES_PATH, os.path.abspath(Config.DATA_FILES_PATH), downloadable=False)
UploadController(app, ['/upload'])
