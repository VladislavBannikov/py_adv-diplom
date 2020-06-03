import json

user_fixtures = r"..\fixtures\users.json"


def get_id_screen_name():
    with open(user_fixtures, encoding="utf-8") as f:
        users = json.load(f)
    name_id = {}
    for i in users.get('response').get('items'):
        name_id.update({i.get('screen_name'): i.get('id')})
    return name_id


def get_info():
    with open(user_fixtures, encoding="utf-8") as f:
        users = json.load(f)
    # id_info = {}
    # for i in users.get('response').get('items'):
    #     id_info.update({i.get('id'): i})
    return users.get('response').get('items')
