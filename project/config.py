import os
#default config
class Config():
    DEBUG = False
    SECRET_KEY = os.environ['SEC_KEY_DASH_PROJ']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['DB_URL_DASH_PROJ']


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']