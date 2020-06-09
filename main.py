from vk.vk_module import VKBase
from vk.user_module import User
from vk.vk_utils import search_candidates_users, score_candidates
import db.db_orm
import json
import os
from settings import VK_COUNT_TO_FIND
from user_info_helper import ask_additional_info, all_info_fields

info_message = '''u - Select lonely user
s - Search new candidates for lonely user
i - show lonely user info 
p - update lonely user info (books, interests, birth date)
t - Top 10 scored candidates (from local database)
r - delete all data from local database
q - for exit
'''
cmd_list = ("u", "r", "t", "s", "q", "i", "p")

# Test Users ----------
# 'svetlana_belyaeva_photographer'
# ---------------------

find_count = VK_COUNT_TO_FIND


def output_result(cand_score1):
    print(os.linesep, "Best candidates for lonely user:")
    with open("out.json", "w", encoding="utf-8") as f:
        json_result = []
        out_pattern = '{:<40}{:<10}{:<40}{:<10}{:<120}'
        if cand_score1:
            print(out_pattern.format("Name", "Fr. count", "Link", "Score", "Photos"))
        for cs in cand_score1:
            photos = cs[0].get_photos()
            j_out = {"first_last_name": cs[0].get_first_last_name(),
                     "friends_count": cs[0].get_friends_count(),
                     "user_url": str(cs[0]),
                     "score": round(cs[1], 2),
                     "photos_id": photos}
            json_result.append(j_out)
            print(out_pattern.format(j_out['first_last_name'],
                                     j_out['friends_count'],
                                     j_out['user_url'],
                                     j_out['score'],
                                     str(photos)))
        f.write(json.dumps(json_result, indent=True))


if __name__ == '__main__':
    VKBase.test_vk_connection_with_prompt()
    db = db.db_orm.dbvk

    lonely_user: User = None
    lonely_user = User('585578161')


    def print_candidate_count_for_user(user_id):
        already_checked_users_ids = db.get_candidates_id(user_id)
        print("Numer of scored candidates in database:", len(
            already_checked_users_ids))


    def check_lonely_user_selected():
        if not lonely_user:
            print("Please select lonely user")
            return False
        return True


    print(info_message)
    while 1:
        cmd = input(f"[User:{lonely_user}] SELECT ACTION:\n").lower()
        if cmd in cmd_list:
            if cmd == 'q':
                exit(0)
            elif cmd == 'r':  # delete all data from local database;
                db.delete_all()
            elif cmd == 'u':  # select lonely user
                lonely_user = User(input("Enter lonely user id or screen name:").strip())
                if lonely_user.is_closed():
                    print('''Your profile is private. Accuracy of search will be low. We advice you to open the profile
                             and repeat the search. You can continue now with low accuracy.''')
                print_candidate_count_for_user(lonely_user.get_id())
            elif cmd == 'p':  # update info (books, interests, birth date)
                if not check_lonely_user_selected():
                    continue
                ask_additional_info(lonely_user, all_info_fields)
            elif cmd == 'i':  # show lonely user info
                if not check_lonely_user_selected():
                    continue
                out_pattern = '{:<30}{:<100}'
                print("Lonely user info:")
                for k, v in lonely_user.get_info().items():
                    print(out_pattern.format(k, str(v)))

            elif cmd == 't':  # Top 10 scored candidates (from local database)
                if not check_lonely_user_selected():
                    continue
                best_cand = db.get_top_10_candidates(lonely_user.get_id())
                if not best_cand:
                    print("Candidates not found in local database. Probably you haven't searched yet.")
                    continue
                best_cand = ((User(c[0]), c[1]) for c in best_cand)
                output_result(best_cand)

            elif cmd == 's':  # new search. Find candidates for lonely user;
                if not check_lonely_user_selected():
                    continue

                if not lonely_user.get_is_additional_info_requested():
                    empty_fields = lonely_user.check_info_completeness()
                    if empty_fields:
                        ask_additional_info(lonely_user, empty_fields)

                ## find candidates and its score
                print_candidate_count_for_user(lonely_user.get_id())
                candidates = search_candidates_users(lonely_user, db.get_candidates_id(lonely_user.get_id()),
                                                     find_count=find_count)
                print("Found new candidates for lonely user", len(candidates))
                print("Retrieving  info about users...")
                User.update_friends_batch(candidates)
                User.update_groups_batch(candidates)
                print("Scoring users...")
                cand_score = score_candidates(lonely_user, candidates)

                ## record result to database
                infos = [c.get_info() for c in candidates]
                if not (db.get_info_by_id(lonely_user.get_id())):  # add lonely user to database if isn't there
                    infos.append(lonely_user.get_info())
                db.add_several_users(infos)
                score = ((s[0].get_id(), s[1]) for s in cand_score)
                db.add_score(lonely_user.get_id(), score)

                ##  add photos to DB for 10 users with best match
                for s in cand_score[:10]:
                    db.add_photos(s[0].get_id(), s[0].get_photos())

                output_result(cand_score[:10])
