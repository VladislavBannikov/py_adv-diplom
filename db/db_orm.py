from sqlalchemy import create_engine, Integer, Column, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import system_settings


Base = declarative_base()


class __DBVK():
    """
    create db connection and check if db and tables are exist
    Note: to check tables are exist run init_database() at the bottom of the module
    """
    DB_NAME = 'vk_'+system_settings.VK_APP_ID

    def __init__(self):
        self.engine = None
        self.session = None
        # self.conn = None
        self.db_connect()

    def db_connect(self):
        conn_string_vk_db = 'postgresql://{}:{}@localhost/{}'.format(system_settings.DB_ADMIN_USER, system_settings.DB_ADMIN_PASSWORD, self.DB_NAME)
        conn_string_postgres_db = 'postgresql://{}:{}@localhost/{}'.format(system_settings.DB_ADMIN_USER, system_settings.DB_ADMIN_PASSWORD,
                                                                         "postgres")

        # check if VK_* database exists, create if doesn't
        try:
            engine_postgres = create_engine(conn_string_postgres_db)
            conn = engine_postgres.connect()
            sql_text = text("SELECT datname FROM pg_database where datname = :db_name;")
            rs = conn.execute(sql_text, db_name=self.DB_NAME)
            if rs.rowcount == 0:
                conn.execute("commit")
                sql_text = text(f"create database {self.DB_NAME};")  #TODO: parameter substitution doesn't work for CREATE, sql.identifier should help
                conn.execute(sql_text)
            conn.close()
        except Exception as e:
            print(f'Error during creation database {self.DB_NAME}:', e)
            exit(1)

        # connect to VK_* database
        try:
            #  Create session
            self.engine = create_engine(conn_string_vk_db)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except Exception as e:
            print('Error during connection to database {self.DB_NAME}:', e)
            exit(1)


__dbvk = __DBVK()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=False)
    info = Column(JSONB)
    photos = Column(JSONB)

    def __str__(self):
         return self.info


class Score(Base):
    __tablename__ = 'score'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    candidate_id = Column(Integer, ForeignKey("user.id"))
    score = Column(Float, nullable=False)
    user = relationship("User", foreign_keys="Score.user_id")
    candidate = relationship("User", foreign_keys="Score.candidate_id")


def get_ids():
    """
    :return: all user's in in db (list)
    """
    users = __dbvk.session.query(User).all()
    return [u.id for u in users]


def get_candidates_id(user_id):
    """
    :param user_id:
    :return: list of candidates id
    """
    cand_ids = __dbvk.session.query(Score.candidate_id).filter(Score.user_id == user_id).all()
    return_candidates = [i for i, in cand_ids]

    cand_ids = __dbvk.session.query(Score.user_id).filter(Score.candidate_id == user_id).all()
    return_candidates = return_candidates + [i for i, in cand_ids]

    return return_candidates


def get_top_10_candidates(user_id):
    cand_ids = __dbvk.session.query(Score.candidate_id, Score.score).filter(Score.user_id==user_id).order_by(Score.score.desc()).all()
    return cand_ids[:10]


def add_score(user_id: Integer, cand_score: list):
    """
    Add scores to database
    :param user_id: lonely user id
    :param cand_score: candidates with score related to lonely user (list of [candidate id, score])
    :return: no return
    """
    for cs in cand_score:
        rec = Score(user_id=user_id, candidate_id=cs[0], score=cs[1])
        __dbvk.session.add(rec)
    __dbvk.session.commit()


def get_info_by_id(user_id):
    """
    :param user_id:
    :return: info (dict, json) or None
    """
    u = __dbvk.session.query(User).get(user_id)
    if u:
        return u.info
    else:
        return None


def add_users(info):
    """
    Add users to database
    :param info: List of user info (dict, json)
    :return: No return
    """
    for i in info:
        u = User(id=i.get('id'), info=i)
        __dbvk.session.add(u)
    __dbvk.session.commit()


def update_info(user_id, info):
    """
    Update info for particular user
    :param user_id: pk in User table
    :param info: info (JSON/dict format)
    :return: No return
    """
    user = __dbvk.session.query(User).get(user_id)
    if user:
        user.info = info
        __dbvk.session.commit()
    else:
        raise Exception (f"User id {user_id} not found in db")


def add_photos(user_id, photos):
    """
    Add information about photo to user
    :param user_id:
    :param photos: Info about photo in dict, json.
    :return: No return
    """
    x = __dbvk.session.query(User).get(user_id)
    x.photos = photos
    __dbvk.session.commit()


def get_photos(user_id):
    """
    :param user_id:
    :return: photos (dict, json) or None
    """
    x = __dbvk.session.query(User).get(user_id)
    if x:
        return x.photos
    else:
        return None


def del_users():
    """
    Clean up User table
    :return: No return
    """
    __dbvk.session.query(User).delete()
    __dbvk.session.commit()


def del_score():
    """
    Clean up Score table
    :return: No return
    """
    __dbvk.session.query(Score).delete()
    __dbvk.session.commit()


def init_database():
    """
    Create all tables
    :return: No return
    """
    Base.metadata.create_all(__dbvk.engine)


def delete_all():
    """
    Delete all tables
    :return: No return
    """
    Base.metadata.drop_all(__dbvk.engine)


if __name__ == '__main__':
    pass
else:
    init_database()




