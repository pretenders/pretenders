LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file'],
    },

    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s:%(name)s:%(lineno)d: %(message)s'
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': 'pretenders.log',
            'formatter': 'verbose'
        },
    }
}


RUN_MAINTAINER = True
TIMEOUT_PRETENDER = 120

try:
    from local_settings import *
except ImportError:
    pass

LOGGING_STARTED = False
