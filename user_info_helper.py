import datetime
from vk.user_module import User


def __validate_date(date_text: str):
    try:
        datetime.datetime.strptime(date_text, '%d.%m.%Y')
    except ValueError:
        return False
    return True


def __validate_text(text: str):
    if text.strip:
        return True
    else:
        return False


for_loop_info = {"books": {"msg": "Enter books (comma separated)", "val_func": __validate_text},
                 "interests": {"msg": "Enter interests (comma separated)", "val_func": __validate_text},
                 "bdate": {"msg": "Enter birth date (in dd.mm.yyyy format)", "val_func": __validate_date}}

all_info_fields = for_loop_info.keys()


def ask_additional_info(user: User, empty_fields):
    new_info = {}
    for kind in empty_fields:
        user_input = input(for_loop_info.get(kind).get("msg") + ":")
        val_func = for_loop_info.get(kind).get("val_func")
        if val_func(user_input):
            new_info.update({kind: user_input})

        user.update_info_from_dict(new_info, db_write=True)
        user.set_is_additional_info_requested(True)
