from VK.VK import VK
import datetime
from dateutil.relativedelta import relativedelta
import db.db_orm
import copy

vk = VK()


class User:
    """
    to create User object parameter user (userID or dict with user properties) is required
    query DB to check if user already there and retrieve info
    """
    __FIELDS_TO_GET = 'is_closed, books, city, has_photo, interests, sex, relation, bdate'
    __PHOTOS = []
    __IS_PHOTO_INIT = False

    def __init__(self, user):
        user_local_var = copy.copy(user)
        self.__IS_INFO_INIT = False
        self.__INFO = dict()

        # TODO: optimize this mess
        # check if info already in DB
        if isinstance(user_local_var, str) or isinstance(user_local_var, int):
            if str(user_local_var).isdigit():
                info_from_db = db.db_orm.get_info_by_id(user_local_var)
                if info_from_db:
                    user_local_var = info_from_db

        if isinstance(user_local_var, int):
            self.__ID = str(user_local_var)
        elif isinstance(user_local_var, str):  # if screen_name convert to ID
            if user_local_var.isdigit():
                self.__ID = user_local_var
            else:
                self.__ID = str(User.screen_name_to_id(user_local_var))
        elif isinstance(user_local_var, dict):  # if dict assign to user_info
            self.__ID = user_local_var.get('id')
            self.__INFO = user_local_var
            self.__IS_INFO_INIT = True

        self.__FRIENDS = []  # list of User class
        self.__GROUPS = {}  # list of group IDs in ['items']
        self.__IS_FRIENDS_INIT = False
        self.__IS_GROUPS_INIT = False

    @staticmethod
    def screen_name_to_id(name):
        """
        Query VK API to get user ID
        :param name: VK user screen_name
        :return: VK user ID
        """
        params = {'screen_name': name}
        return vk.vk_request(method='utils.resolveScreenName', params=params).get('object_id')

    def load_info_from_vk(self):
        """
        update user info
        :return: True if success
        """
        user = self.load_users([self.get_id()], is_get_info=True)[0]

        if user:
            self.__INFO = user.get_info()
            self.__IS_INFO_INIT = True
            return True
        else:
            raise Exception(r"Can't get user info", self.get_id())

    @classmethod
    def load_users(cls, user_ids, is_get_info=False):
        """
        Create User classes from list of IDs
        :param user_ids: list of IDs
        :param is_get_info: if True, query VK for user info
        :return: list of Users classes
        """

        if not isinstance(user_ids, list):
            raise Exception('parameter user_ids should be the list of IDs')

        users = []
        if not is_get_info:  # create Users with ID only, not query to VK
            for uid in user_ids:
                users.append(User(uid))
        else:           # create Users with info, query to VK
            user_ids = ','.join(str(i) for i in user_ids)
            params = {
                'user_ids': user_ids,
                'fields': cls.__FIELDS_TO_GET
            }
            users_info = vk.vk_request(method='users.get', params=params)
            for user_info in users_info:
                users.append(User(user_info))
        return users

    def update_friends(self):
        """
        Load friends list from VK
        :return:  No return
        """
        params = {
            'user_id': self.get_id(),
        }
        response = vk.vk_request(method='friends.get', params=params)
        friends_id = response.get('items')
        self.__FRIENDS = friends_id
        self.__IS_FRIENDS_INIT = True

    def update_groups(self):
        """
        Load groups list from VK
        :return: No return
        """
        params = {
            'user_id': self.get_id(),
        }
        response = vk.vk_request(method='groups.get', params=params)
        self.__GROUPS = response.get('items')
        self.__IS_GROUPS_INIT = True

    def update_photos(self):
        """
        Load 3 most liked photos from VK
        :return: No return
        """
        params = {
            "owner_id": self.get_id(),
            "album_id": "profile",
            "extended": "1",
            "count": "1000"
        }
        photos_info = vk.vk_request('photos.get', params=params).get('items')
        photos_id_likes = []
        for pi in photos_info:
            photos_id_likes.append({"photo_id": pi.get('id'), "likes": pi.get('likes').get('count')})
        photos_id_likes.sort(key=lambda x: x.get('likes'), reverse=True)
        self.__PHOTOS = photos_id_likes[:3]
        self.__IS_PHOTO_INIT = True

    @classmethod
    def update_friends_batch(cls, users):
        """
        Load friends list for users. Use batch execution to VK
        :param users: List of User classes
        :return: No return
        """

        # determine users_id which friends_list is not loaded
        no_friends = []
        for u in users:
            if not u.get_is_friends_initiated():
                no_friends.append(u.get_id())

        # retrieve friends in format [[user_id[<list of friends_id>]],...]
        retrieved_ids = (vk.vk_request_batch("friends.get", no_friends))

        # validate result and update friends_list for every user
        if not len(users) == len(retrieved_ids):
            raise Exception("retrieved_ids count doesn't match users count")
        else:
            for i in range(len(users)):
                if not users[i].get_id() == retrieved_ids[i][0]:
                    raise Exception("id in retrieved data doesn't match with user id")
                else:
                    users[i].update_friends_from_list(retrieved_ids[i][1])

    @classmethod
    def update_groups_batch(cls, users):
        """
        Load groups list for users. Use batch execution to VK
        :param users: List of User classes
        :return: No return
        """

        # determine users_id which group_list is not loaded
        no_groups = []
        for u in users:
            if not u.get_is_groups_initiated():
                no_groups.append(u.get_id())

        # retrieve groups in format [[user_id[<list of groups_id>]],...]
        retrieved_ids = (vk.vk_request_batch("groups.get", no_groups))

        # validate result and update groups_list for every user
        if not len(users) == len(retrieved_ids):
            raise Exception("retrieved_ids count doesn't match users count")
        else:
            for i in range(len(users)):
                if not users[i].get_id() == retrieved_ids[i][0]:
                    raise Exception("id in retrieved data doesn't match with user id")
                else:
                    users[i].update_groups_from_list(retrieved_ids[i][1])

    def update_groups_from_list(self, list):
        self.__GROUPS = list
        self.__IS_GROUPS_INIT = True

    def update_friends_from_list(self, list):
        self.__FRIENDS = list
        self.__IS_FRIENDS_INIT = True

    def update_info_from_dict(self, info: dict, db_write=False):
        self.__INFO.update(info)
        if db_write:
            db.db_orm.update_info(self.get_id(), self.get_info())

    def check_info_completeness(self):
        """
        Check if user have all required fields
        :return: return list of fields without information
        """

        keys = ["books", "interests"]  # TODO: make this as property of module
        user_info = self.get_info()
        empty_info = []
        for k in keys:
            if not user_info.get(k, None):
                empty_info.append(k)
        if not self.get_age():
            empty_info.append('bdate')
        return empty_info

# ==========getters============
    def get_id(self):
        return self.__ID

    def is_closed(self):
        return self.get_info().get('is_closed', True)

    def is_can_access_closed(self):
       return self.get_info().get('can_access_closed', False)

    def is_deleted(self):
        return bool(self.get_info().get('deactivated', None))

    def get_city_title(self):
        c = self.get_info().get('city', None)
        if c:
            return c.get('title', None)
        else:
            return None

    def get_city_id(self):
        c = self.get_info().get('city', None)
        if c:
            return c.get('id', None)
        else:
            return None

    def get_gender(self):
        return self.get_info().get('sex')

    def get_gender_partner(self):
        if self.get_gender() == 1:
            g = 2
        elif self.get_gender() == 2:
            g = 1
        else:
            g = 0
        return g

    def get_age(self):
        d_now = datetime.datetime.now()
        try:
            d_user = datetime.datetime.strptime(self.get_info().get('bdate'), '%d.%M.%Y')
        except (ValueError, TypeError):
            return None
        return relativedelta(d_now, d_user).years

    def get_relation(self):
        """
        1 — не женат/не замужем;
        2 — есть друг/есть подруга;
        3 — помолвлен/помолвлена;
        4 — женат/замужем;
        5 — всё сложно;
        6 — в активном поиске;
        7 — влюблён/влюблена;
        8 — в гражданском браке;
        0 — не указано.
        """
        return self.get_info().get('relation')

    def get_friends(self):
        if not self.__IS_FRIENDS_INIT:
            self.update_friends()
        return self.__FRIENDS

    def get_is_friends_initiated(self):
        return self.__IS_FRIENDS_INIT

    def get_is_groups_initiated(self):
        return self.__IS_GROUPS_INIT

    def get_groups(self):
        if not self.__IS_GROUPS_INIT:
            self.update_groups()
        return self.__GROUPS

    def get_books(self):
        return self.get_info().get('books', None)

    def get_interests(self):
        return self.get_info().get('interests', None)

    def get_photos(self):
        if not self.__IS_PHOTO_INIT:
            photo_from_db = db.db_orm.get_photos(self.get_id())
            if photo_from_db:
                self.__PHOTOS = photo_from_db
            else:
                self.update_photos()
                db.db_orm.add_photos(self.get_id(), self.__PHOTOS)
            self.__IS_PHOTO_INIT = True
        return self.__PHOTOS

    def get_info(self) -> dict:
        if not self.__IS_INFO_INIT:
            self.load_info_from_vk()
        return self.__INFO

    @classmethod
    def get_fields_to_get(cls):
        return cls.__FIELDS_TO_GET
# ==================/getters============

    def __and__(self, other):
        return set(self.__FRIENDS) & set(other.get_friends())

    def __str__(self):
        return f'https://vk.com/id{self.get_id()}'

    def __repr__(self):
        return f'https://vk.com/id{self.get_id()}'




