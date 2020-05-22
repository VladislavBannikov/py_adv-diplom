from VK.VK import VK
from VK.User import User
from VK.VK_utils import search_candidates_users, check_info_completeness, score_candidates
import db.db_orm
import json
import os

# settings
__COUNT_TO_FIND = 1000
__IS_DEBUG = False


info_message = '''n - new search. Find candidates for lonely user;
i - init (reset) database;
t - generate new VK access token;
q - for exit
'''
cmd_list = ["n", "i", "t", "q"]

# Test Users ----------
# 'svetlana_belyaeva_photographer'
# ---------------------


def out_result(cand_score1):
    print(os.linesep, "Best candidates for lonely user:")
    with open("out.json", "w", encoding="utf-8") as f:
        json_result = []
        for cs in cand_score1:
            j_out = {"user_url": str(cs[0]), "score": cs[1], "photos_id": [p.get("photo_id") for p in db.db_orm.get_photos(cs[0].get_id())]}
            json_result.append(j_out)
            print(j_out)
        f.write(json.dumps(json_result, indent=True))


if __name__ == '__main__':
    vk = VK()
    vk.set_is_debug(__IS_DEBUG)

    print(info_message)
    while 1:
        cmd = input("SELECT ACTION:\n").lower()
        if cmd in cmd_list:
            if cmd == 'q':
                exit(0)
            elif cmd == 'i':  # init (reset) database;
                db.db_orm.delete_all()
                db.db_orm.init_database()
                # db.db_orm.del_score()  # drop records from  Score table
                # db.db_orm.del_users()  # drop records from  User table
            elif cmd == 't':  # generate new VK access token;
                print(vk.generate_new_token())
                print("User link above to generate VK access token. Create file token.key in app directory.")
            elif cmd == 'n':  # new search. Find candidates for lonely user;
                lonely_user = User(input("Enter lonely user id or screen name:").strip())
                # lonely_user = User('585578161')
                check_info_completeness(lonely_user)

                ## find candidates and its score
                already_checked_users_ids = db.db_orm.get_ids()
                print("Candidates for lonely user already checked:", len(
                    already_checked_users_ids))  # technically is it -1 (sometimes), because lonely user also in db (usually). I don't care
                candidates = search_candidates_users(lonely_user, already_checked_users_ids, count_to_find=__COUNT_TO_FIND)
                print("Found new candidates for lonely user", len(candidates))
                User.update_friends_batch(candidates)
                User.update_groups_batch(candidates)
                cand_score = score_candidates(lonely_user, candidates)

                ## record result to database
                infos = [c.get_info() for c in candidates]
                if not (db.db_orm.get_info_by_id(lonely_user.get_id())):  # add lonely user to database if isn't there
                    infos.append(lonely_user.get_info())
                db.db_orm.add_users(infos)
                db.db_orm.add_score(lonely_user.get_id(), [[s[0].get_id(), s[1]] for s in cand_score])

                ##  add photos to DB for 10 users with best match
                for s in cand_score:
                    db.db_orm.add_photos(s[0].get_id(), s[0].get_photos())

                out_result(cand_score)

