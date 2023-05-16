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
from sqlalchemy.orm import relationship, as_declarative
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

    def __repr__(self) -> str:
        return f"<user id=\"{self.id}\" email=\"{self.email}\" role=\"{self.role}\">"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    @classmethod
    def create(cls, first_name: str, last_name: str) -> 'Author':
        try:
            with databaseConfig.Session() as session:
                existing_author = session.query(Author).filter((Author.first_name.lower() == first_name.lower()) & (Author.last_name.lower() == last_name.lower())).first()
                if existing_author is None:
                    author = cls(
                        first_name=first_name.title(),
                        last_name=last_name.title(),
                    )
                    session.add(author)
                    session.commit()
                    LOGGER.info(f"Created author: {author}")
                else:
                    LOGGER.warning(f"Author already exists in database: {existing_author}")
                return session.query(Author).filter((Author.first_name.lower() == first_name.lower()) & (Author.last_name.lower() == last_name.lower())).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating author: {e}")
            raise e

    def __repr__(self) -> str:
        return f"<Author id=\"{self.id}\" name=\"{self.first_name} {self.last_name}\">"

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    publisher_name = Column(String, nullable=False)
    city = Column(String, nullable=False)

    @classmethod
    def create(cls, publisher_name: str, city: str) -> 'Publisher':
        try:
            with databaseConfig.Session() as session:
                existing_publisher = session.query(Publisher).filter((Publisher.publisher_name == publisher_name) & (Publisher.city == city)).first()
                if existing_publisher is None:
                    publisher = cls(
                        publisher_name=publisher_name.title(),
                        city=city.capitalize(),
                    )
                    session.add(publisher)
                    session.commit()
                    LOGGER.info(f"Created publisher: {publisher}")
                else:
                    LOGGER.warning(f"Publishers already exists in database: {existing_publisher}")
                return session.query(Publisher).filter((Publisher.publisher_name == publisher_name) & (Publisher.city == city)).first()
        except IntegrityError as e:
            LOGGER.error(e.orig)
            raise e.orig
        except SQLAlchemyError as e:
            LOGGER.error(f"Unexpected error when creating publisher: {e}")
            raise e

    def __repr__(self) -> str:
        return f"<Publisher id=\"{self.id}\" publisher_name=\"{self.publisher_name}\">"

    def __str__(self) -> str:
        return f"{self.publisher_name}, {self.city}"


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement="auto")
    book_name = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"), nullable=False)
    publish_year = Column(Integer)
    volume = Column(Integer)

    # Relationships
    author = relationship("Author")
    publisher = relationship("Publisher")

    @classmethod
    def create(cls, book_name: str, author: Author, publisher: Publisher, publish_year: int = None, volume: int = None) -> 'Book':
        try:
            book = cls(
                book_name=book_name.title(),
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

    def __repr__(self) -> str:
        return f"<Book id=\"{self.id}\" book_name=\"{self.book_name}\"" + ((" volume=\"" + str(self.volume) + "\"") if self.volume != None else "") + ">"

    def __str__(self) -> str:
        return self.book_name


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

    def __repr__(self) -> str:
        return f"<Request id=\"{self.id}\" book=\"{self.book_id}\" user=\"{self.user_id}\">"


if __name__ == '__main__':
    response = input("[WARNING] Do you want to create the database tables? [y] ~> ")
    if response.lower() == 'y':
        Base.metadata.create_all(databaseConfig.engine)
        print('Database created.')
    else:
        print('Canceled.')
