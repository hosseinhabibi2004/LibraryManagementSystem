from datetime import date, datetime
from sqlalchemy import (
    inspect,
    Column,
    Integer,
    String,
    DateTime,
    Date,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship, as_declarative, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import databaseConfig, userRoles
from utils import hash_password
from logger import LOGGER


@as_declarative()
class Base:
    @classmethod
    def get_by_id(cls, id: int):
        with databaseConfig.Session() as session:
            return session.query(cls).get(id)

    def update(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        
        with databaseConfig.Session() as session:
            session.commit()

    def delete(self):
        if self:
            with databaseConfig.Session() as session:
                session.delete(self)
                session.commit()
            LOGGER.info(f'delete: {self}')
            return True
        return False

    def as_dict(self):
        return {column.key: getattr(self, column.key) for column in inspect(self).mapper.column_attrs}


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f"<user id=\"{self.id}\" email=\"{self.email}\" role=\"{self.role}\">"

    @classmethod
    def create(cls, id: int, email: str, first_name: str, last_name: str, role: str = userRoles.STUDENT) -> 'User':
        try:
            with databaseConfig.Session() as session:
                existing_user = session.query(User).filter((User.id == id) & (User.email == email)).first()
                if existing_user is None:
                    user = cls(
                        id=id,
                        email=email,
                        first_name=first_name.title(),
                        last_name=last_name.title(),
                        password=hash_password(str(id)),
                        role=role,
                    )
                    session.add(user)
                    session.commit()
                    LOGGER.info(f"Created user: {user}")
                else:
                    LOGGER.warning(f"User already exists in database: {existing_user}")
                return session.query(User).filter(User.id == id).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating user: {e}")
            raise e

    def update_password(self, password: str) -> bool:
        self.password = hash_password(password)
        with databaseConfig.Session() as session:
            session.add(self)
            session.commit()
            return True


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Author id=\"{self.id}\" name=\"{self.first_name} {self.last_name}\">"

    @classmethod
    def create(cls, session: Session, first_name: str, last_name: str):
        try:
            with databaseConfig.Session() as session:
                existing_author = session.query(Author).filter((Author.first_name == first_name) & (Author.last_name == last_name)).first()
                if existing_author is None:
                    author = cls(
                        first_name=first_name.capitalize(),
                        last_name=last_name.capitalize(),
                    )
                    session.add(author)
                    session.commit()
                    LOGGER.info(f"Created author: {author}")
                else:
                    LOGGER.warning(f"Author already exists in database: {existing_author}")
                return session.query(Author).filter((Author.first_name == first_name) & (Author.last_name == last_name)).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating author: {e}")
            raise e


class Publisher(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)

    def __repr__(self):
        return f"<Publisher id=\"{self.id}\" name=\"{self.name}\">"

    @classmethod
    def create(cls, session: Session, name: str, city: str):
        try:
            with databaseConfig.Session() as session:
                existing_publisher = session.query(Publisher).filter((Publisher.name == name) & (Publisher.city == city)).first()
                if existing_publisher is None:
                    publisher = cls(
                        name=name.title(),
                        city=city.capitalize(),
                    )
                    session.add(publisher)
                    session.commit()
                    LOGGER.info(f"Created publisher: {publisher}")
                else:
                    LOGGER.warning(f"Publishers already exists in database: {existing_publisher}")
                return session.query(Publisher).filter((Publisher.name == name) & (Publisher.city == city)).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating publisher: {e}")
            raise e


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    name = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=False)
    publish_year = Column(Integer)
    volume = Column(Integer)

    # Relationships
    author = relationship("Author")
    publisher = relationship("Publisher")

    def __repr__(self):
        return f"<Book id=\"{self.id}\" name=\"{self.name}\"" + ((" volume=\"" + str(self.volume) + "\"") if self.volume != None else "") + ">"

    @classmethod
    def create(cls, name: str, author: Author, publisher: Publisher, publish_year: int = None, volume: int = None):
        try:
            book = cls(
                name=name.title(),
                author=author,
                publisher=publisher,
                publish_year=publish_year,
                volume=volume,
            )
            with databaseConfig.Session() as session:
                session.add(book)
                session.commit()
                LOGGER.info(f"Created book: {book}")
                return session.query(Book).filter(Book.id == book.id).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating book: {e}")
            raise e


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delivery_date = Column(Date, default=date.today())
    receive_date = Column(Date)
    status = Column(Boolean, default=False)

    # Relationships
    book = relationship("Book")
    user = relationship("User")

    def __repr__(self):
        return f"<Request id=\"{self.id}\" book=\"{self.book_id}\" user=\"{self.user_id}\">"

    @classmethod
    def create(cls, book: Book, user: User, receive_date: date):
        try:
            request = cls(
                book=book,
                user=user,
                receive_date=receive_date,
            )
            with databaseConfig.Session() as session:
                session.add(request)
                session.commit()
                LOGGER.info(f"Created request: {request}")
                return session.query(Request).filter(Request.id == request.id).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating request: {e}")
            raise e


if __name__ == '__main__':
    response = input("[WARNING] Do you want to create the database tables? [y] ~> ")
    if response.lower() == 'y':
        Base.metadata.create_all(databaseConfig.engine)
        print('Database created.')
    else:
        print('Canceled.')
