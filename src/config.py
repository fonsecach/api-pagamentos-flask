import os
from abc import ABC, abstractmethod


class Config(ABC):
    """Base configuration class."""
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    
    @property
    @abstractmethod
    def SQLALCHEMY_DATABASE_URI(self):
        """Database URI must be implemented by subclasses."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f'sqlite:///{os.path.join(self.basedir, "..", "instance", "database.db")}'


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        uri = os.environ.get('DATABASE_URL')
        if not uri:
            basedir = os.path.abspath(os.path.dirname(__file__))
            uri = f'sqlite:///{os.path.join(basedir, "..", "instance", "database.db")}'
        return uri


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
