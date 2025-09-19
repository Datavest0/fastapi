from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

#  Import if you want to connect and run SQL querys directly
# import psycopg
# from psycopg.rows import dict_row
# import time

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


#  TO connect and run SQLquerys directly.
# while True:

#     try:
#         conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='@Miracle007', row_factory=dict_row)
#         cursor = conn.cursor()
#         print('successful')
#         break
#     except Exception as error:
#         print('connection failed')
#         print("Error:", error)
#         time.sleep(2)