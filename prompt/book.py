from datetime import date
from prompt_toolkit.shortcuts import (
    message_dialog,
    yes_no_dialog,
    radiolist_dialog,
    button_dialog,
    input_dialog
)
from prompt_toolkit.formatted_text import HTML
from sqlalchemy.orm import joinedload

from . import styles, author, publisher
from config import baseConfig, databaseConfig
from models import User, Book, Author, Publisher, Request


def search_books() -> Book:
    while True:
        book_name = input_dialog(
            title="Search Books",
            text="Enter a book name:",
        ).run()

        if not book_name:
            return None

        with databaseConfig.Session() as session:
            books = session.query(Book).options(joinedload(Book.author)).filter(Book.book_name.ilike(f'%{book_name}%')).all()

        if books:
            selected_book = radiolist_dialog(
                title="Search Books",
                text="Select a book:",
                values=[(book, f"{book.book_name}, {book.author.first_name} {book.author.last_name}") for book in books],
            ).run()
            if selected_book:
                return selected_book
            else:
                message_dialog(
                    title="Search Books | Error",
                    text="No book selected.",
                    style=styles.ERROR
                ).run()
        else:
            message_dialog(
                title="Search Books | Error",
                text="No books found.",
                style=styles.ERROR
            ).run()


def add_book() -> Book:
    book_info = {
        'book_name': None,
        'author': None,
        'publisher': None,
        'publish_year': None,
        'volume': None,
    }

    while True:
        for field_name in book_info:
            if book_info[field_name] is None:
                default_option = field_name
                break
            else:
                default_option = 'done'

        values = [(field_name, HTML('<style fg="#5DA7DB"><b>' + field_name.replace('_', ' ').title().ljust(len(max(book_info.keys(), key=len))) + (('</b></style> <style fg="#5DA7DB"><i>' + str(book_info[field_name]) + '</i></style>') if book_info[field_name] != None else ('</b></style>')))) for field_name in book_info]
        values.append(('done', HTML('<style fg="#5DA7DB"><b>Done</b></style>')))

        selected_option = radiolist_dialog(
            title='Add Book',
            text='Please enter your information:',
            values=values,
            default=default_option,
            style=styles.BLUE,
        ).run()

        if selected_option == 'book_name':
            book_info['book_name'] = get_valid_book_name()
        elif selected_option == 'author':
            author_selected = button_dialog(
                title='Select Author',
                text='Add or search author.',
                buttons=[
                    ('Add', 'add_author'),
                    ('Search', 'search_author'),
                    ('Back', None)
                ],
                style=styles.BLUE,
            ).run()
            if author_selected == 'add_author':
                book_info['author'] = author.add_author()
            elif author_selected == 'search_author':
                book_info['author'] = author.search_authors()
            else:
                continue
        elif selected_option == 'publisher':
            publisher_selected = button_dialog(
                title='Select Publisher',
                text='Add or search publisher.',
                buttons=[
                    ('Add', 'add_publisher'),
                    ('Search', 'search_publisher'),
                    ('Back', None)
                ],
                style=styles.BLUE,
            ).run()
            if publisher_selected == 'add_publisher':
                book_info['publisher'] = publisher.add_publisher()
            elif publisher_selected == 'search_publisher':
                book_info['publisher'] = publisher.search_publishers()
            else:
                continue
        elif selected_option == 'publish_year':
            book_info['publish_year'] = get_valid_publish_year()
        elif selected_option == 'volume':
            book_info['volume'] = get_valid_volume()
        elif selected_option == 'done':
            if None not in [book_info[field_name] for field_name in ['book_name', 'author', 'publisher']]:
                return Book.create(
                    book_name=book_info['book_name'],
                    author=book_info['author'],
                    publisher=book_info['publisher'],
                    publish_year=book_info['publish_year'],
                    volume=book_info['volume'],
                )
            else:
                should_edit = yes_no_dialog(
                    title='Add Book',
                    text='Your information is incomplete. Would you like to edit it?',
                    no_text='Exit',
                    style=styles.WARNING,
                ).run()
                if should_edit:
                    continue
                else:
                    return None
        else:
            return None


def update_book(book: Book) -> Book:
    book_info = book.as_dict()

    while True:
        values = []
        for field_name, field_value in book_info.items():
            if field_name not in ['id']:
                if field_name == 'author_id':
                    field_name = 'author'
                    field_value = Author.get_by_id(book_info['author_id'])
                elif field_name == 'publisher_id':
                    field_name = 'publisher'
                    field_value = Publisher.get_by_id(book_info['publisher_id'])
                values.append((field_name, HTML('<style fg="#5DA7DB"><b>' + field_name.replace('_', ' ').title().ljust(len(max(book_info.keys(), key=len))) + (('</b></style> <style fg="#5DA7DB"><i>' + str(field_value) + '</i></style>') if field_value != None else ('</b></style>'))), ))
        values.append(('done', HTML('<style fg="#5DA7DB"><b>Done</b></style>'), ))

        selected_option = radiolist_dialog(
            title='Update Book',
            text='Please enter your information:',
            values=values,
            style=styles.BLUE,
        ).run()

        if selected_option == 'book_name':
            book_info['book_name'] = get_valid_book_name()
        elif selected_option == 'author':
            author_selected = button_dialog(
                title='Select Author',
                text='Add or search author.',
                buttons=[
                    ('Add', 'add_author'),
                    ('Search', 'search_author'),
                    ('Back', None)
                ],
                style=styles.BLUE,
            ).run()
            if author_selected == 'add_author':
                book_info['author'] = author.add_author()
            elif author_selected == 'search_author':
                book_info['author'] = author.search_authors()
            else:
                continue
        elif selected_option == 'publisher':
            publisher_selected = button_dialog(
                title='Select Author',
                text='Add or search publisher.',
                buttons=[
                    ('Add', 'add_publisher'),
                    ('Search', 'search_publisher'),
                    ('Back', None)
                ],
                style=styles.BLUE,
            ).run()
            if publisher_selected == 'add_publisher':
                book_info['publisher'] = publisher.add_publisher()
            elif publisher_selected == 'search_publisher':
                book_info['publisher'] = publisher.search_publishers()
            else:
                continue
        elif selected_option == 'publish_year':
            book_info['publish_year'] = get_valid_publish_year()
        elif selected_option == 'volume':
            book_info['volume'] = get_valid_volume()
        elif selected_option == 'done':
            if None not in [book_info[field_name] for field_name in ['book_name', 'author_id', 'publisher_id']]:
                return book.update(**book_info)
            else:
                should_edit = yes_no_dialog(
                    title='Update Book',
                    text='Your information is incomplete. Would you like to edit it?',
                    no_text='Exit',
                    style=styles.WARNING,
                ).run()
                if should_edit:
                    continue
                else:
                    return None
        else:
            return None


def delete_book(book: Book) -> bool:
    delete_book_yes_no = yes_no_dialog(
        title='Delete Book',
        text='Are you delete this book?',
        style=styles.WARNING,
    ).run()
    if delete_book_yes_no:
        return book.delete()
    return False


def reserve_book(user_id: int) -> Request:
    with databaseConfig.Session() as session:
        current_user_reservations = session.query(Request).filter(Request.return_date == None).filter(Request.user_id == user_id).count()

    if current_user_reservations >= baseConfig.MAX_RESERVATIONS_LIMIT:
        message_dialog(
            title="Reserve Book",
            text=f"You have already reached the maximum limit of {baseConfig.MAX_RESERVATIONS_LIMIT} reservations.",
            style=styles.ERROR,
        ).run()
        return

    selected_book = search_books()
    if selected_book:
        with databaseConfig.Session() as session:
            is_reserved = selected_book.is_reserved()
            if is_reserved:
                message_dialog(
                    title="Reserve Book",
                    text="The selected book is already reserved.",
                    style=styles.ERROR,
                ).run()
                return

            request = Request.create(book=selected_book, user=User.get_by_id(user_id))
            if request:
                message_dialog(
                    title="Reserve Book",
                    text="Book reserved successfully.",
                    style=styles.SUCCESS,
                ).run()
                return request
    else:
        message_dialog(
            title="Reserve Book",
            text="No available books found.",
            style=styles.ERROR,
        ).run()


def return_book(request_id):
    with databaseConfig.Session() as session:
        request = (
            session.query(Request)
            .filter(Request.id == request_id)
            .options(joinedload(Request.book))
            .one()
        )

    book_name = request.book.book_name if request.book else "Unknown Book"
    confirmation = yes_no_dialog(
        title="Return Book",
        text=f"Are you sure you want to return the book '{book_name}'?",
        style=styles.BLUE,
    ).run()

    if not confirmation:
        return

    request.update(return_date=date.today())

    message_dialog(
        title="Return Book",
        text="Book returned successfully.",
        style=styles.SUCCESS,
    ).run()


def show_reserved_books(user_id):
    with databaseConfig.Session() as session:
        unreturned_books = (
            session.query(Request)
            .filter(Request.user_id == user_id)
            .filter(Request.return_date == None)
            .options(joinedload(Request.book))
            .all()
        )

    if not unreturned_books:
        message_dialog(
            title="Reserved Books",
            text="You have no reserved books.",
            style=styles.ERROR,
        ).run()
        return

    selected_book = radiolist_dialog(
        title="Reserved Books",
        text="Select a book to return:",
        values=[(str(request.id), request.book.book_name) for request in unreturned_books if request.book],
        style=styles.BLUE,
    ).run()

    if not selected_book:
        return

    return return_book(int(selected_book))


def get_valid_book_name():
    """
    Prompt the user to enter a valid book name.
    """
    book_name = input_dialog(
        title='Add Book',
        text='Please enter your book name:',
        style=styles.BLUE,
    ).run()

    if not book_name or book_name.strip() == '':
        return None
    return book_name.strip().title()


def get_valid_publish_year():
    """
    Prompt the user to enter a valid publish year.
    """
    while True:
        publish_year = input_dialog(
            title='Add Book',
            text='Please enter publish year:',
            style=styles.BLUE,
        ).run()
        if not publish_year or publish_year.strip() == '':
            return None
        elif publish_year.isdigit() and len(publish_year)==4:
            if 1900 <= int(publish_year) <= date.today().year:
                return int(publish_year)
        message_dialog(
            title='Add Book | Error',
            text='Please enter a valid year.',
            style=styles.ERROR
        ).run()


def get_valid_volume():
    """
    Prompt the user to enter a valid volume.
    """
    while True:
        volume = input_dialog(
            title='Add Book',
            text='Please enter volume:',
            style=styles.BLUE,
        ).run()
        if not volume or volume.strip() == '':
            return None
        elif volume.isdigit():
            return int(volume)
        else:
            message_dialog(
                title='Add Book | Error',
                text='Please enter a valid number.',
                style=styles.ERROR
            ).run()
