from prompt_toolkit.shortcuts import radiolist_dialog, button_dialog
from prompt_toolkit.formatted_text import HTML

from . import styles, book
from models import Author, Publisher


def manager_menu():
    while True:
        selected_option = radiolist_dialog(
            title="Manager Menu",
            text="Select Option",
            values=[
                ("add_book", "Add Book"),
                ("search_book", "Search Book"),
            ],
            cancel_text="Exit",
            style=styles.BLUE,
        ).run()

        if selected_option=="add_book":
            book.add_book()
        elif selected_option=="search_book":
            selected_book = book.search_books()
            while True:
                selected_book_info = selected_book.as_dict()
                text = '<style fg="#9254C8">'
                for field_name, field_value in selected_book_info.items():
                    if field_name not in ['id']:
                        if field_name == 'author_id':
                            field_name = 'author'
                            field_value = Author.get_by_id(selected_book_info['author_id'])
                        elif field_name == 'publisher_id':
                            field_name = 'publisher'
                            field_value = Publisher.get_by_id(selected_book_info['publisher_id'])

                        if field_value != None:
                            text +=  f"<b>{field_name.replace('_', ' ').title().replace('Id', 'ID').ljust(len(max(selected_book_info.keys(), key=len)))}</b> : <i>{str(field_value).replace('_', ' ').title()}</i>\n"
                text += '</style>'

                author_selected = button_dialog(
                    title='Book Details',
                    text=HTML(text),
                    buttons=[
                        ('Update', 'update_book'),
                        ('Delete', 'delete_book'),
                        ('Back', None)
                    ],
                    style=styles.BLUE,
                ).run()
                if author_selected == 'update_book':
                    updated_book = book.update_book(selected_book)
                    if updated_book:
                        selected_book = updated_book
                    else:
                        break
                elif author_selected == 'delete_book':
                    if book.delete_book(selected_book):
                        break
                    else:
                        continue
                else:
                    break
        elif selected_option==None:
            break
