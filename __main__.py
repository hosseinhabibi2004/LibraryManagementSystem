from prompt_toolkit.shortcuts import (
    button_dialog
)

from prompt import styles, sign_in, sign_up, manager_menu, student_menu
from config import userRoles


if __name__=='__main__':
    while True:
        signin_signup_selected = button_dialog(
            title='Sign In | Sign Up',
            text='Sign In or Sign Up?',
            buttons=[
                ('Sign In', 'sign_in'),
                ('Sign Up', 'sign_up'),
                ('Exit', None)
            ],
            style=styles.BLUE,
        ).run()
        if signin_signup_selected=="sign_in":
            user = sign_in()
            if user:
                break
        elif signin_signup_selected=="sign_up":
            user = sign_up()
            if user:
                break
        else:
            break

    if user.role == userRoles.MANAGER:
        manager_menu(user.id)
    elif user.role == userRoles.STUDENT:
        student_menu(user.id)
