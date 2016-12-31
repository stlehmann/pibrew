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
    PROCESS_INTERVAL = 0.1  # interval for brew controller processing
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DATABASE_FILENAME = 'pibrew-devel.sqlite'
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = False
    LOG_LEVEL = logging.DEBUG
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:////' + os.path.join(basedir, 'data-dev.sqlite')


class ProductionConfig(Config):
    DATABASE_FILENAME = 'pibrew.sqlite'
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or \
        'sqlite:////' + os.path.join(basedir, 'data-prod.sqlite')


class TestingConfig(Config):
    WTF_CSRF_ENABLED = False
    DATABASE_FILENAME = 'pibrew-test.sqlite'
    LOG_LEVEL = logging.ERROR
    TESTING = True
    SIMULATE = True
    PROCESS_INTERVAL = 0.1  # interval for brew controller processing
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:////' + os.path.join(basedir, 'data-test.sqlite')


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
