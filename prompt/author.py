from prompt_toolkit.shortcuts import (
    message_dialog,
    yes_no_dialog,
    radiolist_dialog,
    input_dialog
)
from prompt_toolkit.formatted_text import HTML
import re

from . import styles
from config import databaseConfig
from models import Author


def search_authors():
    while True:
        author_name = input_dialog(
            title="Search Authors",
            text="Enter a author name:",
        ).run()

        if not author_name:
            return None

        with databaseConfig.Session() as session:
            authors = session.query(Author).filter((Author.first_name + ' ' + Author.last_name).ilike(f'%{author_name}%')).all()

        if authors:
            selected_author = radiolist_dialog(
                title="Search Authors",
                text="Select a author:",
                values=[(author, f"{author.first_name} {author.last_name}") for author in authors],
            ).run()
            if selected_author:
                return selected_author
            else:
                message_dialog(
                    title="Search Authors | Error",
                    text="No author selected.",
                    style=styles.ERROR
                ).run()
        else:
            message_dialog(
                title="Search Authors | Error",
                text="No authors found.",
                style=styles.ERROR
            ).run()


def add_author():
    author_info = {
        'first_name': None,
        'last_name': None,
    }

    while True:
        for field_name in author_info:
            if author_info[field_name] is None:
                default_option = field_name
                break
            else:
                default_option = 'done'

        values = [(field_name, HTML('<style fg="#5DA7DB"><b>' + field_name.replace('_', ' ').title().ljust(len(max(author_info.keys(), key=len))) + (('</b></style> <style fg="#5DA7DB"><i>' + author_info[field_name] + '</i></style>') if author_info[field_name] != None else ('</b></style>')))) for field_name in author_info]
        values.append(('done', HTML('<style fg="#5DA7DB"><b>Done</b></style>')))

        selected_option = radiolist_dialog(
            title='Add Author',
            text='Please enter your information:',
            values=values,
            default=default_option,
            style=styles.BLUE,
        ).run()

        if selected_option == 'first_name':
            author_info['first_name'] = get_valid_first_name()
        elif selected_option == 'last_name':
            author_info['last_name'] = get_valid_last_name()
        elif selected_option == 'done':
            if None not in author_info.values():
                return Author.create(
                    first_name=author_info['first_name'],
                    last_name=author_info['last_name'],
                )
            else:
                should_edit = yes_no_dialog(
                    title='Add Author',
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


def get_valid_first_name():
    """
    Prompt the user to enter a valid first name.
    """
    while True:
        first_name = input_dialog(
            title='Add Author',
            text='Please enter your first name:',
            style=styles.BLUE,
        ).run()
        if not first_name or first_name.strip() == '':
            return None
        elif re.match(r'^[A-Za-z\s\'-]{2,}$', first_name):
            return first_name.strip().title()
        else:
            message_dialog(
                title='Add Author | Error',
                text='Please enter a valid first name.',
                style=styles.ERROR
            ).run()


def get_valid_last_name():
    """
    Prompt the user to enter a valid last name.
    """
    while True:
        last_name = input_dialog(
            title='Add Author',
            text='Please enter your last name:',
            style=styles.BLUE,
        ).run()
        if not last_name or last_name.strip() == '':
            return None
        elif re.match(r'^[A-Za-z\s\'-]{2,}$', last_name):
            return last_name.strip().title()
        else:
            message_dialog(
                title='Add Author | Error',
                text='Please enter a valid last name.',
                style=styles.ERROR
            ).run()
