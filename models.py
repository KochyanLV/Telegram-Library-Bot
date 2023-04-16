from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, MetaData, Integer, String, Date, Column, ForeignKey
import sqlalchemy_utils
import datetime
from sqlalchemy.orm import sessionmaker

import getpass

Base = declarative_base()
metadata = MetaData()

class Books(Base):
    __tablename__ = 'Books'
    book_id = Column(Integer, primary_key=True, autoincrement = True)
    title = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    published = Column(Integer, nullable=True)
    date_added = Column(Date, nullable=True)
    date_deleted = Column(Date, nullable=True)

class Borrows(Base):
    __tablename__ = 'Borrows'
    borrow_id = Column(Integer, primary_key=True, autoincrement = True)
    book_id = Column(Integer,  ForeignKey('Books.book_id'))
    date_start = Column(Date, nullable=True)
    date_end = Column(Date, nullable=True)
    user_id = Column(Integer, nullable=True)
    book = relationship('Books')

def check_db():
    USERNAME = getpass.getuser()
    connection_string = f"postgresql+psycopg2://{USERNAME}:@localhost:5433/{USERNAME}"
    a = not sqlalchemy_utils.functions.database_exists(connection_string)

    if(a):
        sqlalchemy_utils.functions.create_database(connection_string)

        engine = create_engine(connection_string, echo = True)
        connection = engine.connect()
        engine = create_engine(connection_string)
        Session = sessionmaker(engine)
        session = Session()
        Base.metadata.create_all(engine)
        b = Books(title = "Привет", author = "Это наш бот", published = 2023, date_added = datetime.date.today(), date_deleted = None)
        br = Borrows(book_id = 1, date_start = datetime.date.today(), date_end = datetime.date.today(), user_id = 0)

        session.add(b)
        session.add(br)
        session.commit()

check_db()
