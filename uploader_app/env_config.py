import os

def _get_env(env_var, default):
    """
    Retrieve environmental variable
    or fallback to a default value.
    Input:
      - env_var(string): name of the variable to retrieve
      - default(string): default value to fall back to
    Output:
      - Value of the environmental variable or default
        value in case the variable is not defined in the enviroment.
        The return always has the same type as the default value
    """
    try:
        tp = type(default)
        return tp(os.environ[env_var])
    except:
        return default


class Config:
    """
    Config is a class with the general
    geoserver configurations
    """

    ## General configurations

    # LOG FORMATTING
    LOG_FORMAT = _get_env("LOG_FORMAT", "%(asctime)s - %(levelname)s: %(message)s")

    # PATHS
    LOGS_PATH = _get_env("LOGS_PATH", "logs")
    DATA_PATH = _get_env("DATA_PATH", "data")

    DATA_TEMP_PATH = _get_env("DATA_TEMP_PATH", "data/temp")
    DATA_FILES_PATH = _get_env("DATA_FILES_PATH", "data/files")

    # HOST
    HOST = _get_env("HOST", "localhost")

    ## App

    APP_LOG = _get_env("APP_LOG", "app.log")

    APP_HOST = _get_env("APP_HOST", "localhost")

    APP_BIND_ADDRESS = _get_env("APP_BIND_ADDRESS", "0.0.0.0:3010")

    #APP_WORKERS = _get_env("APP_WORKERS", 2)
    #APP_TIMEOUT = _get_env("APP_TIMEOUT", 3000)
    #APP_LIMIT_REQUEST_FIELD_SIZE = _get_env("LIMIT_REQUEST_FIELD_SIZE", 0)

    UPLOAD_SERVICE_CHUNK_SIZE = _get_env("UPLOAD_SERVICE_CHUNK_SIZE", 10000)
