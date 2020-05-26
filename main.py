from VK.VK import VK
from VK.User import User
from VK.VK_utils import search_candidates_users, score_candidates
import db.db_orm
import json
import os
import settings

info_message = '''u - Select lonely user
s - Search new candidates for lonely user;
t - Top 10 scored candidates (from local database)
r - reset database;
q - for exit
'''
cmd_list = ["u", "r", "t", "s", "q"]
lonely_user: User = None
# lonely_user = User('585578161')

# Test Users ----------
# 'svetlana_belyaeva_photographer'
# ---------------------


def output_result(cand_score1):
    print(os.linesep, "Best candidates for lonely user:")
    with open("out.json", "w", encoding="utf-8") as f:
        json_result = []
        out_pattern = '{:<40}{:<10}{:<120}'
        if cand_score1:
            print(out_pattern.format("Link", "Score", "Photos"))
        for cs in cand_score1:
            photos = cs[0].get_photos()
            j_out = {"user_url": str(cs[0]), "score": round(cs[1], 2), "photos_id": photos}
            json_result.append(j_out)
            print(out_pattern.format(j_out['user_url'], j_out['score'], str(photos)))
        f.write(json.dumps(json_result, indent=True))


if __name__ == '__main__':
    vk = VK()
    # db.db_orm.get_top_10_candidates(lonely_user.get_id())

    def print_candidate_count_for_user(user_id):
        already_checked_users_ids = db.db_orm.get_candidates_id(user_id)
        print("Numer of scored candidates in database:", len(
            already_checked_users_ids))

    def ask_additional_info(empty_fields):
        message = {"books": "Enter books (comma separated)",
                   "interests": "Enter interests (comma separated)",
                   "bdate": "Enter birth date (in dd.mm.yyyy format)"
                   }
        new_info = {}
        for field_key in empty_fields:
            # TODO: add validation
            new_info.update({field_key: input(message[field_key] + ":")})
        lonely_user.update_info_from_dict(new_info, db_write=True)

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
            elif cmd == 'r':  # init (reset) database;
                db.db_orm.delete_all()
                db.db_orm.init_database()
            elif cmd == 'u':  # select lonely user
                lonely_user = User(input("Enter lonely user id or screen name:").strip())
                print_candidate_count_for_user(lonely_user.get_id())
            elif cmd == 't':  # Top 10 scored candidates (from local database)
                if not check_lonely_user_selected():
                    continue
                best_cand = db.db_orm.get_top_10_candidates(lonely_user.get_id())
                best_cand =[[User(c[0]),c[1]] for c in best_cand]
                output_result(best_cand)

            elif cmd == 's':  # new search. Find candidates for lonely user;
                if not check_lonely_user_selected():
                    continue

                while True:
                    empty_fields = lonely_user.check_info_completeness()
                    if not empty_fields:
                        break
                    ask_additional_info(empty_fields)


                ## find candidates and its score
                print_candidate_count_for_user(lonely_user.get_id())
                candidates = search_candidates_users(lonely_user, db.db_orm.get_candidates_id(lonely_user.get_id()), count_to_find=settings.VK_COUNT_TO_FIND)
                print("Found new candidates for lonely user", len(candidates))
                print("Retrieving  info about users...")
                User.update_friends_batch(candidates)
                User.update_groups_batch(candidates)
                print("Scoring users...")
                cand_score = score_candidates(lonely_user, candidates)

                ## record result to database
                infos = [c.get_info() for c in candidates]
                if not (db.db_orm.get_info_by_id(lonely_user.get_id())):  # add lonely user to database if isn't there
                    infos.append(lonely_user.get_info())
                db.db_orm.add_users(infos)
                db.db_orm.add_score(lonely_user.get_id(), [[s[0].get_id(), s[1]] for s in cand_score])

                ##  add photos to DB for 10 users with best match
                for s in cand_score[:10]:
                    db.db_orm.add_photos(s[0].get_id(), s[0].get_photos())

                output_result(cand_score[:10])

