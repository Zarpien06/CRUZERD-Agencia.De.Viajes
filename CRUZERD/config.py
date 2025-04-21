import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-cruzerd-app'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/CRUZERD"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


