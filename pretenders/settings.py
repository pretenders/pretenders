LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'DEBUG',
        'handlers': ['console'],
    },

    'formatters': {
        'verbose': {'format': '%(asctime)s %(levelname)s:%(name)s: %(message)s'},
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    }
}


try:
    from local_settings import *
except ImportError:
    pass
