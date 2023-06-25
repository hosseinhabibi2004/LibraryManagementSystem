from prompt_toolkit.shortcuts import radiolist_dialog, button_dialog, message_dialog
from prompt_toolkit.formatted_text import HTML
from sqlalchemy.orm import joinedload

from . import styles, book, student
from models import User, Author, Publisher, Request
from config import databaseConfig


def manager_menu(manager_id):
    while True:
        selected_option = radiolist_dialog(
            title="Manager Menu",
            text="Select Option",
            values=[
                ("add_book", "Add Book"),
                ("search_book", "Search Book"),
                ("search_user", "Search User"),
                ("show_all_requests", "Show All Requests"),
                ("change_password", "Change Password"),
            ],
            cancel_text="Exit",
            style=styles.BLUE,
        ).run()

        if selected_option=="add_book":
            book.add_book()
        elif selected_option=="search_book":
            selected_book = book.search_books()

            if not selected_book:
                continue

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

                search_book_selected_option = button_dialog(
                    title='Book Details',
                    text=HTML(text),
                    buttons=[
                        ('Update', 'update_book'),
                        ('Delete', 'delete_book'),
                        ('Back', None)
                    ],
                    style=styles.BLUE,
                ).run()
                if search_book_selected_option == 'update_book':
                    updated_book = book.update_book(selected_book)
                    if updated_book:
                        selected_book = updated_book
                    else:
                        break
                elif search_book_selected_option == 'delete_book':
                    if book.delete_book(selected_book):
                        break
                    else:
                        continue
                else:
                    break
        elif selected_option=="search_user":
            selected_user = student.search_student_by_id()

            if not selected_user:
                continue

            while True:
                selected_user_info = selected_user.as_dict()
                text = '<style fg="#9254C8">'
                for field_name, field_value in selected_user_info.items():
                    if field_name not in ['password']:
                        if field_name=='updated_by_user_id':
                            field_name = 'updated_by_user_id'
                            field_value = User.get_by_id(selected_user_info['updated_by_user_id'])
                        if field_value == None:
                            field_value = ''
                        text +=  f"<b>{field_name.replace('_', ' ').title().replace('Id', 'ID').ljust(len(max(selected_user_info.keys(), key=len)))}</b> : <i>{str(field_value)}</i>\n"
                text += '</style>'

                search_user_selected_option = button_dialog(
                    title='User Details',
                    text=HTML(text),
                    buttons=[
                        ('Penalty', 'penalty'),
                        ('Requests', 'requests'),
                        ('Password', 'password'),
                        ('Back', None)
                    ],
                    style=styles.BLUE,
                ).run()
                if search_user_selected_option=="penalty":
                    penalty = student.calculate_penalty(selected_user.id)
                    message_dialog(
                        title="Show Penalty",
                        text=f"The student's penalty is ${penalty}.",
                        style=styles.GREEN,
                    ).run()
                elif search_user_selected_option == 'requests':
                    student.show_student_requests(selected_user.id)
                elif search_user_selected_option == 'password':
                    updated_user = student.change_password(selected_user.id, manager_id, False)
                    if updated_user:
                        selected_user = updated_user
                else:
                    break
        elif selected_option=="show_all_requests":
            with databaseConfig.Session() as session:
                requests = (
                    session.query(Request)
                    .options(joinedload(Request.book))
                    .options(joinedload(Request.user))
                    .all()
                )
            if not requests:
                message_dialog(
                    title="User Requests",
                    text="No requests found.",
                    style=styles.BLUE,
                ).run()
                continue

            request_info = "\n".join([f"User: {str(request.user)}, Book: {request.book.book_name if request.book else 'Unknown Book'}, Delivery Date: {request.delivery_date}, Return Date: {request.return_date if request.return_date else 'Not returned'}" for request in requests])
            message_dialog(
                title="User Requests",
                text=request_info,
                style=styles.BLUE,
            ).run()
        elif selected_option=="change_password":
            student.change_password(manager_id, manager_id)
        elif selected_option==None:
            break
