from datetime import date
from prompt_toolkit.shortcuts import (
    message_dialog,
    radiolist_dialog,
    input_dialog,
    yes_no_dialog,
)
from sqlalchemy.orm import joinedload
import re

from . import styles, book
from models import User, Request
from config import databaseConfig, userRoles
from utils import check_password


def student_menu(user_id):
    while True:
        selected_option = radiolist_dialog(
            title="Student Menu",
            text="Select Option",
            values=[
                ("reserve_book", "Reserve Book"),
                ("show_reserved_books", "Show Reserved Book"),
                ("show_penalty", "Show Penalty"),
                ("show_requests", "Show Requests"),
                ("change_password", "Change Password"),
            ],
            cancel_text="Exit",
            style=styles.BLUE,
        ).run()


        if selected_option == 'reserve_book':
            book.reserve_book(user_id)
        elif selected_option == 'show_reserved_books':
            book.show_reserved_books(user_id)
        elif selected_option == 'show_penalty':
            penalty = calculate_penalty(user_id)
            message_dialog(
                title="Show Penalty",
                text=f"The student's penalty is ${penalty}.",
                style=styles.GREEN,
            ).run()
        elif selected_option == 'show_requests':
            show_student_requests(user_id)
        elif selected_option == 'change_password':
            change_password(user_id, user_id)
        else:
            break


def change_password(user_id: int, updated_by_user_id: int, get_old_password: bool = True) -> None:
    password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&\.])[A-Za-z\d@$!%*?&\.]{8,}$"
    user = User.get_by_id(user_id)

    while get_old_password:
        old_password = input_dialog(
            title='Change Password',
            text='Please type your old password:',
            password=True,
            style=styles.PINK,
        ).run()
        if not old_password:
            return None
        elif check_password(old_password, user.password):
            get_old_password = False
        else:
            message_dialog(
                title='Change Password | Error',
                text='Password is incorrect.\nPlease try again.',
                style=styles.ERROR,
            ).run()

    while True:
        new_password = input_dialog(
            title='Change Password',
            text='Please type new password:',
            password=True,
            style=styles.PINK,
        ).run()

        if not new_password:
            return None
        elif re.match(password_regex, new_password):
            while True:
                new_password_again = input_dialog(
                    title='Change Password',
                    text='Please type new password again:',
                    password=True,
                    cancel_text='Back',
                    style=styles.PINK,
                ).run()

                if not new_password_again:
                    break
                elif new_password==new_password_again:
                    user.update_password(new_password, updated_by_user_id)
                    message_dialog(
                        title='Change Password',
                        text='Your password successfully changed.',
                        style=styles.SUCCESS,
                    ).run()
                    return user
                else:
                    message_dialog(
                        title='Change Password | Error',
                        text='Password is incorrect.\nPlease try again.',
                        style=styles.ERROR,
                    ).run()
        else:
            message_dialog(
                title='Change Password | Error',
                text='Password is not strong.\nPlease write stronger password.',
                style=styles.ERROR,
            ).run()


def search_student_by_id() -> User:
    while True:
        user_id = input_dialog(
            title="Search Student",
            text="Enter Student ID:"
        ).run()

        if not user_id:
            return None

        with databaseConfig.Session() as session:
            user = session.query(User).filter(User.role == userRoles.STUDENT).filter(User.id == user_id).first()

            if user:
                confirmation = yes_no_dialog(
                    title="Search Student",
                    text=f"Student found: {str(user)}. Do you want to proceed?",
                    style=styles.WARNING,
                ).run()

                if confirmation:
                    return user
            else:
                message_dialog(
                    title="Search Student",
                    text="Student not found.",
                    style=styles.ERROR,
                ).run()


def calculate_penalty(user_id):
    with databaseConfig.Session() as session:
        requests = (
            session.query(Request)
            .filter(Request.user_id == user_id)
            .all()
        )

    total_penalty = 0
    for request in requests:
        return_date = request.return_date or date.today()
        return_deadline = request.return_deadline
        timedelta_diff = return_date - return_deadline

        if timedelta_diff.days > 0:
            penalty = timedelta_diff.days * 10
            total_penalty += penalty

    return total_penalty


def show_student_requests(user_id):
    with databaseConfig.Session() as session:
        requests = (
            session.query(Request)
            .filter(Request.user_id == user_id)
            .options(joinedload(Request.book))
            .all()
        )
    if not requests:
        message_dialog(
            title="User Requests | Error",
            text="No requests found for the user.",
            style=styles.ERROR,
        ).run()
        return

    request_info = "\n".join([f"Book: {request.book.book_name if request.book else 'Unknown Book'}, Delivery Date: {request.delivery_date}, Return Date: {request.return_date if request.return_date else 'Not returned'}" for request in requests])
    message_dialog(
        title="User Requests",
        text=request_info,
        style=styles.BLUE,
    ).run()
