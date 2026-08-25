class Config:

    SQLALCHEMY_DATABASE_URI = "sqlite:///rbac.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = "rbac-mvp-secret-key"