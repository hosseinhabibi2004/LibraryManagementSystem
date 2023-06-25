import re
import bcrypt


def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def check_isbn(isbn: str):
    # Checks for ISBN-10 or ISBN-13 format
    regex = re.compile("^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$")

    if regex.search(isbn.upper()):
        # Remove non ISBN digits, then split into a list
        chars = list(re.sub("[- ]|^ISBN(?:-1[03])?:?", "", isbn.upper()))
        # Remove the final ISBN digit from `chars`, and assign it to `last`
        last = chars.pop()

        if len(chars) == 9:
            # Compute the ISBN-10 check digit
            val = sum((x + 2) * int(y) for x,y in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:
            # Compute the ISBN-13 check digit
            val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"

        if (str(check) == last):
            # convert the ISBN-10 to ISBN-13
            if len(chars) == 9:
                chars = ['9', '7', '8'] + chars
                val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
                check = 10 - (val % 10)
                if check == 10:
                    check = "0"
            return True, ''.join(chars) + str(check)
        else:
            return False, ''.join(chars) + str(check)
    else:
        return False, None
