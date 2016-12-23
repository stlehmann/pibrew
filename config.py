import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SIMULATE = False
    LOG_LEVEL = logging.WARNING
    SECRET_KEY = os.environ.get('SECRET_KEY',
                                '9844f8c4eebfc08ed88cd3d64f201db3')
    PROCESS_INTERVAL = 1.0  # interval for brew controller processing


class DevelopmentConfig(Config):
    DATABASE_FILENAME = 'pibrew-devel.sqlite'
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = False
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    DATABASE_FILENAME = 'pibrew.sqlite'
    pass


class TestingConfig(Config):
    WTF_CSRF_ENABLED = False
    DATABASE_FILENAME = 'pibrew-test.sqlite'
    TESTING = True
    SIMULATE = True
    PROCESS_INTERVAL = 0.1  # interval for brew controller processing


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
