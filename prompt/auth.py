from prompt_toolkit.shortcuts import (
    message_dialog,
    yes_no_dialog,
    radiolist_dialog,
    input_dialog,
)
from prompt_toolkit.formatted_text import HTML
import re

from . import styles
from models import User
from utils import check_password
from config import databaseConfig


def sign_in() -> User:
    """
    Prompt the user to sign in with their email and password.
    Returns a User object if the email and password are valid, or None if the user cancels or enters invalid information.
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    while True:
        email = input_dialog(
            title='Sign In',
            text='Please enter your email address:',
            style=styles.BLUE,
        ).run()

        if not email or email.strip() == '':
            return None

        if not re.match(email_pattern, email):
            message_dialog(
                title='Sign In | Error',
                text='Invalid email address.\nPlease try again.',
                style=styles.ERROR
            ).run()
            continue

        with databaseConfig.Session() as session:
            user = session.query(User).filter(User.email == email.lower()).first()

        while True:
            password = input_dialog(
                title='Sign In',
                text='Please type your password: [default: Student ID]',
                password=True,
                style=styles.BLUE
            ).run()

            if password is None:
                break

            if check_password(password.strip(), user.password):
                return user
            else:
                message_dialog(
                    title='Sign In | Error',
                    text='Incorrect password!\nPlease try again.',
                    style=styles.ERROR
                ).run()


def sign_up() -> User:
    """
    Prompt the user to sign up by entering their student ID, email address, first name, and last name.
    Returns a new User object with the entered information, or None if the user cancels or leaves any fields blank.
    """
    user_info = {
        'student_id': None,
        'email': None,
        'first_name': None,
        'last_name': None,
    }

    while True:
        for field_name in user_info.keys():
            if user_info[field_name] is None:
                default_option = field_name
                break
            else:
                default_option = 'done'

        selected_option = radiolist_dialog(
            title='Sign Up',
            text='Please enter your information:',
            values=[
                ('student_id',  HTML('<style fg="#5DA7DB"><b>Student Identification Number'.ljust(53)   + (('</b></style> <style fg="#5DA7DB"><i>' + user_info["student_id"] + '</i></style>') if user_info["student_id"] != None else ('</b></style>')))),
                ('email',       HTML('<style fg="#5DA7DB"><b>Email'.ljust(53)                           + (('</b></style> <style fg="#5DA7DB"><i>' + user_info["email"]      + '</i></style>') if user_info["email"]      != None else ('</b></style>')))),
                ('first_name',  HTML('<style fg="#5DA7DB"><b>First Name'.ljust(53)                      + (('</b></style> <style fg="#5DA7DB"><i>' + user_info["first_name"] + '</i></style>') if user_info["first_name"] != None else ('</b></style>')))),
                ('last_name',   HTML('<style fg="#5DA7DB"><b>Last Name'.ljust(53)                       + (('</b></style> <style fg="#5DA7DB"><i>' + user_info["last_name"]  + '</i></style>') if user_info["last_name"]  != None else ('</b></style>')))),
                ('done',        HTML('<style fg="#5DA7DB"><b>Done</b></style>'))
            ],
            default=default_option,
            style=styles.BLUE,
        ).run()

        if selected_option == 'student_id':
            user_info['student_id'] = get_valid_student_id()
        elif selected_option == 'email':
            user_info['email'] = get_valid_email()
        elif selected_option == 'first_name':
            user_info['first_name'] = get_valid_first_name()
        elif selected_option == 'last_name':
            user_info['last_name'] = get_valid_last_name()
        elif selected_option == 'done':
            if None not in user_info.values():
                return User.create(
                    id=user_info['student_id'],
                    email=user_info['email'],
                    first_name=user_info['first_name'],
                    last_name=user_info['last_name'],
                )
            else:
                should_edit = yes_no_dialog(
                    title='Sign Up',
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


def get_valid_student_id() -> int:
    """
    Prompt the user to enter a valid student identification number.
    Returns the entered student ID as an integer if it is valid and not already in use by another user, or None if the user cancels or enters invalid information.
    """
    student_id_pattern = r'^\d{9,11}$'
    while True:
        student_id = input_dialog(
            title='Sign Up',
            text='Please enter your student identification number:',
            style=styles.BLUE,
        ).run()

        if not student_id:
            return None
        elif re.match(student_id_pattern, student_id):
            with databaseConfig.Session() as session:
                if session.query(User).filter(User.id == student_id).count() == 0:
                    return int(student_id)
                else:
                    message_dialog(
                        title='Sign Up | Error',
                        text='User with that student identification number already exists.\nPlease try again.',
                        style=styles.ERROR
                    ).run()
        else:
            message_dialog(
                title='Sign Up | Error',
                text='Invalid student identification number.\nPlease try again.',
                style=styles.ERROR
            ).run()


def get_valid_email() -> str:
    """
    Prompt the user to enter a valid email address.
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    while True:
        email = input_dialog(
            title='Sign Up',
            text='Please enter your email address:',
            style=styles.BLUE,
        ).run()

        if not email or email.strip() == '':
            return None
        elif re.match(email_pattern, email):
            with databaseConfig.Session() as session:
                if session.query(User).filter(User.email == email).count() == 0:
                    return email
                else:
                    message_dialog(
                        title='Sign Up | Error',
                        text='Email address already exists.\nPlease try again.',
                        style=styles.ERROR
                    ).run()
        else:
            message_dialog(
                title='Sign Up | Error',
                text='Invalid email address.\nPlease try again.',
                style=styles.ERROR
            ).run()


def get_valid_first_name() -> str:
    """
    Prompt the user to enter a valid first name.
    Returns the entered first name as a string if it is valid, or None if the user cancels or enters invalid information.
    """
    while True:
        first_name = input_dialog(
            title='Sign Up',
            text='Please enter your first name:',
            style=styles.BLUE,
        ).run()
        if not first_name or first_name.strip() == '':
            return None
        elif re.match(r'^[A-Za-z\s\'-]{2,}$', first_name):
            return first_name.strip().title()
        else:
            message_dialog(
                title='Sign Up | Error',
                text='Please enter a valid first name.',
                style=styles.ERROR
            ).run()


def get_valid_last_name() -> str:
    """
    Prompt the user to enter a valid last name.
    Returns the entered last name as a string if it is valid, or None if the user cancels or enters invalid information.
    """
    while True:
        last_name = input_dialog(
            title='Sign Up',
            text='Please enter your last name:',
            style=styles.BLUE,
        ).run()
        if not last_name or last_name.strip() == '':
            return None
        elif re.match(r'^[A-Za-z\s\'-]{2,}$', last_name):
            return last_name.strip().title()
        else:
            message_dialog(
                title='Sign Up | Error',
                text='Please enter a valid last name.',
                style=styles.ERROR
            ).run()
