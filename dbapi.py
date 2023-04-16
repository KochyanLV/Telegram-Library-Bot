import datetime
from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from models import *
import pandas as pd
import getpass

Base = declarative_base()

class DatabaseConnector:

    class Kekw(Base) :
        __tablename__ = "kekw"
        kekw_id = Column(Integer, primary_key = True, nullable=False)

    def __init__(self, user = getpass.getuser()):

        self.connection_string = f"postgresql+psycopg2://{user}:@localhost:5433/{user}"
        self.engine = create_engine(self.connection_string)
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()
        self.connection = self.engine.connect()

    def add(self, title, author, year):

        try:
            book = Books(title = title, author = author, published = year, date_added = datetime.date.today(),
                         date_deleted = None)

            self.session.add(book)
            self.session.commit()

            query = 'select * from public."Books"'

            idd = 0

            with self.engine.connect() as connection:
                result = pd.read_sql(query, con=connection)

                a = result.to_dict()["book_id"]

                idd = a[len(a) - 1]

            return idd

        except Exception as ex:

            return False

    def delete(self, _id):

        try:
            deletedate = datetime.date.today()

            query = f'select * from public."Borrows" where book_id = {_id}'

            with self.engine.connect() as connection:
                result = pd.read_sql(query, con=connection)

                a = result.to_dict()["date_end"]

                for d in a:
                    if d == None:

                        return False

            self.session.query(Books).filter(Books.book_id == _id).update({Books.date_deleted: deletedate},
                                                                      synchronize_session=False)

            self.session.commit()

            return True


        except Exception as ex:

            return False


    def list_books(self):

        query = f'select title, author, published, date_deleted from public."Books"'

        with self.engine.connect() as connection:
            result = pd.read_sql(query, con=connection)

            a = result.to_dict()
        return a

    def get_book(self, title, author, year):

        d = f'public."Books"'

        query = f"select * from {d}  where title = '{title}' and author = '{author}' and published = {year}"

        with self.engine.connect() as connection:
            result = pd.read_sql(query, con=connection)

            a = result.to_dict()
            res = list(a['book_id'].values())
        return res

    def borrow(self, b_id, u_id):

        try:
            b_id = b_id[0]
            query = f'select * from public."Borrows" where user_id = {u_id}'
            
            with self.engine.connect() as connection:
                result = pd.read_sql(query, con=connection)

                a = result.to_dict()["date_end"]
                ok = False

                for i in a:
                    if a[i] == None:
                        ok = True
                        break

            if(ok):
                return False


            query = f'select * from public."Borrows" where book_id = {b_id}'

            with self.engine.connect() as connection:
                result = pd.read_sql(query, con=connection)

                a = result.to_dict()["date_end"]

                ok = False

                for i in a:
                    if a[i] == None:
                        ok = True
                        break

            if(ok):
                return False


            borrow = Borrows(book_id=b_id, date_start=datetime.date.today(), date_end=None, user_id=u_id)

            self.session.add(borrow)
            self.session.commit()

            query = 'select * from public."Borrows"'

            idd = 0

            with self.engine.connect() as connection:
                result = pd.read_sql(query, con=connection)

                a = result.to_dict()["borrow_id"]

                idd = a[len(a) - 1]

            return idd

        except Exception as ex:
            return False

    def get_borrow(self, u_id):

        query = f'select * from public."Borrows" where user_id = {u_id}'

        with self.engine.connect() as connection:
            result = pd.read_sql(query, con=connection)

            a = result.to_dict()["user_id"]

            idd = a[len(a) - 1]

        return idd

    def retrieve(self, u_id):

        try:
            deletedate = datetime.date.today()

            self.session.query(Borrows).filter(Borrows.user_id == u_id).update({Borrows.date_end: deletedate},
                                                                      synchronize_session=False)

            self.session.commit()
            query = f'select book_id from public."Borrows" where user_id = {u_id}'
            with self.engine.connect() as connection:
                result = pd.read_sql(query, con=connection)
                a = result.to_dict()["book_id"]
                b = 0
                for i in a:
                    b = a[i]
                query_2 = f'select title, author, published from public."Books" where book_id = {b}'
                res = result = pd.read_sql(query_2, con=connection).to_dict()
            return res


        except Exception as ex:
            return False