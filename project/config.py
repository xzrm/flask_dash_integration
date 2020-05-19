import os
#default config
class Config():
    DEBUG = False
    SECRET_KEY = os.environ['SEC_KEY_DASH_PROJ']
    # SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = os.environ['DB_URL_DASH_PROJ']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False