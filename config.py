import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()


class baseConfig:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE_URL = os.getenv('DATABASE_URL')
    MAX_RESERVATIONS_LIMIT = int(os.getenv('MAX_RESERVATIONS_LIMIT'))


class databaseConfig:
    declarativeBase = declarative_base()
    engine = create_engine(baseConfig.DATABASE_URL)
    Session = sessionmaker(bind=engine)


class userRoles:
    STUDENT, MANAGER = 'student', 'manager'
