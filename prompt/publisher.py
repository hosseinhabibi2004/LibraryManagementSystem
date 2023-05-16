from prompt_toolkit.shortcuts import (
    message_dialog,
    yes_no_dialog,
    radiolist_dialog,
    input_dialog
)
from prompt_toolkit.formatted_text import HTML

from . import styles
from config import databaseConfig
from models import Publisher


def search_publishers():
    while True:
        publisher_name = input_dialog(
            title="Search Publishers",
            text="Enter a publisher name:",
        ).run()

        if not publisher_name:
            return None

        with databaseConfig.Session() as session:
            publishers = session.query(Publisher).filter(Publisher.publisher_name.ilike(f'%{publisher_name}%')).all()

        if publishers:
            selected_publisher = radiolist_dialog(
                title="Search Publishers",
                text="Select a publisher:",
                values=[(publisher, f"{publisher.publisher_name}, {publisher.city}") for publisher in publishers],
            ).run()
            if selected_publisher:
                return selected_publisher
            else:
                message_dialog(
                    title="Search Publishers | Error",
                    text="No publisher selected.",
                    style=styles.ERROR
                ).run()
        else:
            message_dialog(
                title="Search Publishers | Error",
                text="No publishers found.",
                style=styles.ERROR
            ).run()


def add_publisher():
    publisher_info = {
        'publisher_name': None,
        'city': None,
    }

    while True:
        for field_name in publisher_info:
            if publisher_info[field_name] is None:
                default_option = field_name
                break
            else:
                default_option = 'done'

        values = [(field_name, HTML('<style fg="#5DA7DB"><b>' + field_name.replace('_', ' ').title().ljust(len(max(publisher_info.keys(), key=len))) + (('</b></style> <style fg="#5DA7DB"><i>' + publisher_info[field_name] + '</i></style>') if publisher_info[field_name] != None else ('</b></style>')))) for field_name in publisher_info]
        values.append(('done', HTML('<style fg="#5DA7DB"><b>Done</b></style>')))

        selected_option = radiolist_dialog(
            title='Add Publisher',
            text='Please enter your information:',
            values=values,
            default=default_option,
            style=styles.BLUE,
        ).run()

        if selected_option == 'publisher_name':
            publisher_info['publisher_name'] = get_valid_name()
        elif selected_option == 'city':
            publisher_info['city'] = get_valid_city()
        elif selected_option == 'done':
            if None not in publisher_info.values():
                return Publisher.create(
                    publisher_name=publisher_info['publisher_name'],
                    city=publisher_info['city'],
                )
            else:
                should_edit = yes_no_dialog(
                    title='Add Publisher',
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


def get_valid_name():
    """
    Prompt the user to enter a valid publisher name.
    """
    name = input_dialog(
        title='Add Publisher',
        text='Please enter your publisher name:',
        style=styles.BLUE,
    ).run()
    if not name or name.strip() == '':
        return None
    return name.strip().title()


def get_valid_city():
    """
    Prompt the user to enter a valid publisher city.
    """
    city = input_dialog(
        title='Add Publisher',
        text='Please enter your publisher city:',
        style=styles.BLUE,
    ).run()
    if not city or city.strip() == '':
        return None
    return city.strip().capitalize()
