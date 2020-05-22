from VK.User import User
from VK.VK import VK
import copy
from random import randint
import os


vk = VK()
__fields_to_check = "bdate, city, sex, books, interests"


def check_info_completeness(user):
    """
    Check if user have all required fields, ask for information
    :param user: User class
    :return: No return
    """
    if not user.get_age():
        bdate = input('Enter birth date (dd.mm.yyyy): ')
        user.update_info1({'bdate': bdate})
    if not user.get_books():
        books = input('Enter books (comma separated): ')
        user.update_info1({'books': books})
    if not user.get_interests():
        interests = input('Enter interests (comma separated): ')
        user.update_info1({'interests': interests})


def find_common(var1, var2) -> int:
    """
    General function to find intersection between var1 and var1
    :param var1: can be list, dict, set, coma separated string
    :param var2: can be list, dict, set, coma separated string
    :return: count of common things
    """
    if not (var1 and var2):  # if either of VAR is None
        return 0
    vars1 = [copy.deepcopy(var1), copy.deepcopy(var2)]
    for vi in range(2):
        if isinstance(vars1[vi], int):
            vars1[vi] = set(str(vars1[vi]))
        if isinstance(vars1[vi], str):
            vars1[vi] = [str(i) for i in vars1[vi].split(',')]
        if isinstance(vars1[vi], list):
            vars1[vi] = set([str(i).lower().strip() for i in vars1[vi]])
        if not isinstance(vars1[vi], set):
            raise Exception('error, vars[vi] is not Set')
    return len(vars1[0] & vars1[1])


def search_candidates_users(user, exclude_ids, delta_age=3, count_to_find=20):
    """
    Find VK users (candidates for lonely user)
    properties: __FIELDS_TO_GET in User class
    :param user: lonely user (User class)
    :param exclude_ids: list of candidates id to exclude from output if any is found. Also close accounts are excluded.
    :param delta_age: Search parameter. +- age from lonely user's age
    :param count_to_find: Search parameter. Count of users to query VK API
    :return: Candidates (List of Users class)
    """
    if vk.get_is_debug():  # debug message
        print(os.linesep, f'[Debug] Search_candidates_users has started')
    if isinstance(user, User):
        if not user.get_gender():
            raise Exception(f'Gender for user {user} not specified')

        params = {
            'count': count_to_find,
            'fields': user.get_fields_to_get(),
            # 'city': user.get_city_id(),
            'birth_day': randint(1, 28),  # workaround VK 1000 limitation
            'birth_month': randint(1, 12),
            'sex': user.get_gender_partner(),
            'age_from': user.get_age() - delta_age,
            'age_to': user.get_age() + delta_age,
            'has_photo': 1
        }
        response = vk.vk_request(method='users.search', params=params)
        candidates = []
        for u_info in response.get('items'):
            candidates.append(User(u_info))

        candidates_copy = candidates[:]
        exclude_ids_set = set(exclude_ids)
        for u in candidates:           # remove bad candidates
            if u.is_closed() or u.get_id() in exclude_ids_set:
                candidates_copy.remove(u)
    return candidates_copy


def score_candidates(user, candidates):
    """
    Compare lonely user with candidates and calc scores
    :param user: Lonely user (User class)
    :param candidates: list of User classes
    :return: Top 10 candidates (list of [candidate: User class, score:float])
    """
    if vk.get_is_debug():  # debug message
        print(os.linesep, f'[Debug] Score_candidates has started')
    u_age = user.get_age()
    u_city_id = user.get_city_id()
    u_gr = set(user.get_groups())
    u_fr = set(user.get_friends())
    u_books = user.get_books()
    u_interests = user.get_interests()
    # (важнее) друзья, возраст, группы, интересы, книги, город (менее важно)
    cand_score = []
    for c in candidates:
        # print(c.get_info())
        score = 0
        # print(c.get_info())
        # print('==u_age', c.get_age())
        if (c.get_city_id() and c.get_city_id() == u_city_id):
            score += 1.1
        if find_common(c.get_books(), u_books) > 0:
            score += 1.2
        if find_common(c.get_interests(), u_interests) > 0:
            score += 1.3
        if find_common(c.get_groups(), u_gr) > 0:
            score += 1.4
        if (c.get_age() and c.get_age() == u_age):
            score += 1.5
        if find_common(c.get_friends(), u_fr) > 0:
            score += 1.6
        # print(c, score)
        cand_score.append([c,score])
    cand_score.sort(key=lambda cand: cand[1], reverse=True)
    return cand_score[:10]


