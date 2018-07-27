import falcon
import logging
import json
import shutil
import os
import sys

from ..env_config import Config

def fbuffer(inputFile, chunk_size = Config.UPLOAD_SERVICE_CHUNK_SIZE,
       logger=None):
   """
   Generator to buffer file chunks
   """
   while True:
       chunk = inputFile.read(chunk_size)
       if not chunk: break
       if logger != None:
           logger.debug("Buffering chunk {}".format(len(chunk)))
       yield chunk


def verify_create_path(input_path, logger=None):
    dirname = os.path.dirname(input_path)
    base_path = ''

    for path in dirname.split('/'):

        base_path = os.path.join(base_path, path)

        if not os.path.exists(base_path):
            try:
                os.mkdir(base_path)

                msg = 'Temporary files path "{}" created'.format(base_path)

                if logger != None:
                    logger.error(msg)
                else:
                    print(msg)

            except:
                msg = 'Temporary files path "{}" could not be created'.format(base_path)

                if logger != None:
                    logger.error(msg)
                else:
                    print(msg)

                raise falcon.HTTPError(falcon.HTTP_500,
                                       'Internal Server Error',
                                       msg)
        else:
            msg = 'Temporary files path "{}" found'.format(base_path)

            if logger != None:
                logger.debug(msg)
            else:
                print(msg)


class UploadController:
    def __init__(self, app, routes, **kwargs):
        for route in routes:
            self.logger = logging.getLogger("Upload Controller")
            msg = "Upload Controller. Adding route {}".format(route)
            self.logger.debug(msg)
            app.add_route(route, self)

        try:
            self.setup()
            self.logger.debug("Upload Controller self.setup ran properly")
        except:
            self.logger.error("Upload Controller self.setup failed to run")
            pass
            # No prepare_log defined

    def get_allowed_methods(self, **kwargs):
        allowed_methods = ['POST']
        return allowed_methods


    def on_get(self, request, response, **kwargs):
        raise falcon.HTTPMethodNotAllowed(self.get_allowed_methods(**kwargs))

    def on_post(self, request, response, **kwargs):
        if not kwargs:
            return self.spawner(request, response)
        raise falcon.HTTPMethodNotAllowed(self.get_allowed_methods(**kwargs))

    def on_put(self, request, response, **kwargs):
        raise falcon.HTTPMethodNotAllowed(self.get_allowed_methods(**kwargs))

    def on_delete(self, request, response, **kwargs):
        raise falcon.HTTPMethodNotAllowed(self.get_allowed_methods(**kwargs))


    def setup(self, temp_path=Config.DATA_TEMP_PATH, final_path=Config.DATA_FILES_PATH):
        global upload_logger

        """
        Sets up the controller. The inherited class BaseController adds the
        routes with its init, and the self.setup runs after that
        """
        # TODO: use the super constructor, and get rid of self.setup

        # Path for the uploads
        self._temp_path = temp_path
        self._final_path = final_path

        upload_logger = logging.getLogger("UploadController")
        self.logger = upload_logger
        self.logger.info("starting Uploader service...")

        self.logger.debug("Upload Controller setup complete")


    def spawner(self, req, resp):
        """
        SPAWNER METHOD

        Request data required:

        'file' : uploaded file
        """
        # Retrieve request params
        input_file = req.get_param('file')

        self.logger.info("Upload requests received")

        # Test if the file was uploaded
        if input_file == None:
            message = "It seems that the uploaded file is empty"
            self.logger.warning(message)
            # Empty file? -> Bad request
            resp.status = falcon.HTTP_400
            resp.body = json.dumps({ "message" : message })
            return

        if not hasattr(input_file, "filename"):
            message = 'No file was uploaded'
            # Log entry
            self.logger.error(message)

            resp.status = falcon.HTTP_400
            resp.body = json.dumps({ "message" : message })
        else:
            self.logger.info("Creating temporary file to store upload")
            # Retrieve filename and extension
            filename, extension = os.path.splitext(input_file.filename)

            filesize = input_file.file.seek(0, os.SEEK_END)

            # Log INFO
            msg = ("File to be uploaded: \n"
                    "filename : {}\tExtension : {}\tSize : {}").format(filename,
                                                                       extension,
                                                                       filesize)
            self.logger.info(msg)

            # Define file_path
            file_path = os.path.join(self._temp_path, filename + extension)

            # Write to a temporary file to prevent incomplete files from
            # being used.
            temp_file_path = file_path + '~'

            # Create the temporary files path if it doesn't exists
            verify_create_path(file_path, logger=self.logger)

            self.logger.debug("Writing to file {}".format(temp_file_path))

            input_file.file.seek(0, 0)
            with open(temp_file_path, 'wb', Config.UPLOAD_SERVICE_CHUNK_SIZE) as output_file:
                # Read the file in chunks
                for chunk in fbuffer(input_file.file):
                    output_file.write(chunk)
                #output_file.close()

            self.logger.debug("Closed the file {}".format(temp_file_path))

            if os.path.getsize(temp_file_path) != filesize:
                message = ("Uploaded and saved files have different sizes:\n"
                           "Uploaded file size : {}\n"
                           "Saved file size: {}\n").format(filesize,
                                                           os.path.getsize(temp_file_path))

                # Send error message and don't save the layer
                self.logger.error(message)
                resp.status = falcon.HTTP_500
                resp.body = json.dumps({ "message" : message })
                return

            # final path
            final_path = os.path.join(self._final_path, filename + extension)

            # Create the files path if it doesn't exists
            verify_create_path(final_path, logger=self.logger)

            try:
                # shutil deals with copies across cross devices
                shutil.move(temp_file_path, final_path)
            except:
                message = ("File could not be saved.\n"
                           "The last exception caught was "
                           "{}").format(sys.exc_info())

                # Log entry
                self.logger.error(message)

                raise falcon.HTTPError(falcon.HTTP_500,
                                       'Internal Server Error',
                                       'Unable to save file')
            else:
                message = 'File uploaded'
                resp.body = json.dumps({ "message" : message })
                resp.status = falcon.HTTP_200
                return
