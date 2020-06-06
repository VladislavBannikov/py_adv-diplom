from sqlalchemy import create_engine, Integer, Column, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from system_settings import VK_APP_ID, DB_ADMIN_USER, DB_ADMIN_PASSWORD
import system_settings
from db.queries import queries as q

Base = declarative_base()


class DBVK():
    """
    create db connection and check if db and tables are exist
    Note: to check tables are exist run init_database() at the bottom of the module
    """

    db_name_vk = 'vk_' + VK_APP_ID
    db_user = DB_ADMIN_USER
    # db_pwd = "3" #DB_ADMIN_PASSWORD
    db_pwd = DB_ADMIN_PASSWORD
    db_host = system_settings.DB_HOSTNAME if hasattr(system_settings, 'DB_HOSTNAME') else 'localhost'

    conn_string_db = f'postgresql://{db_user}:{db_pwd}@{db_host}/'

    def __init__(self):
        self.engine = None
        self.session = None
        self.conn = None

    def check_connection(self):
        """
        Check ability to connect to DB (credentials and hostname)
        :return: bool
        """
        try:
            conn_temp = self.__connect_to_db()
            if conn_temp and not conn_temp.closed:
                conn_temp.close()
                return True
        except Exception:
            return False
        return False

    def get_current_database(self):
        try:
            if self.conn and not self.conn.closed:
                rs = self.conn.execute(q.get_curren_db)
                return rs.fetchone()[0]
        except Exception:
            return None
        return None

    def is_connected_to_vk_db(self):
        if self.get_current_database() == self.db_name_vk:
            return True
        else:
            return False

    def __connect_to_db(self, db_name='postgres'):
        # connect to postgres
        try:
            engine_postgres = create_engine(f"{self.conn_string_db}{db_name}")
            con = engine_postgres.connect()
        except Exception:
            return False
        return con

    def connect_to_vk_db(self):
        try:
            self.conn = self.__connect_to_db(db_name=self.db_name_vk)
            self.engine = self.conn
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            if self.is_connected_to_vk_db():
                return True
        except Exception:
            return False
        return False

    def check_vk_db_exists(self):
        try:
            conn_temp = self.__connect_to_db()
            sql_text = text(q.sel_vk_db)
            rs = conn_temp.execute(sql_text, db_name=self.db_name_vk)
            if rs.rowcount == 1:
                conn_temp.close()
                return True
        except Exception:
            return None
        return False

    def create_vk_db(self):
        try:
            conn_temp = self.__connect_to_db(db_name='postgres')
            conn_temp.execute(q.commit)
            sql_text = text(
                f"create database {self.db_name_vk};")  # TODO: parameter substitution doesn't work for CREATE, sql.identifier should help
            conn_temp.execute(sql_text)
            conn_temp.close()
            if self.check_vk_db_exists():
                return True
        except Exception:
            return None
        return False

    def get_ids(self):
        """
        :return: all user's in in db (list)
        """
        users = self.session.query(User).all()
        return [u.id for u in users]

    def get_candidates_id(self, user_id):
        """
        :param user_id:
        :return: list of candidates id
        """
        cand_ids = self.session.query(Score.candidate_id).filter(Score.user_id == user_id).all()
        return_candidates = [i for i, in cand_ids]

        cand_ids = self.session.query(Score.user_id).filter(Score.candidate_id == user_id).all()
        return_candidates = return_candidates + [i for i, in cand_ids]

        return return_candidates

    def get_top_10_candidates(self, user_id):
        cand_ids = self.session.query(Score.candidate_id, Score.score).filter(Score.user_id == user_id).order_by(
            Score.score.desc()).all()
        return cand_ids[:10]

    def add_score(self, user_id: Integer, cand_score: list):
        """
        Add scores to database
        :param user_id: lonely user id
        :param cand_score: candidates with score related to lonely user (list of [candidate id, score])
        :return: no return
        """
        for cs in cand_score:
            rec = Score(user_id=user_id, candidate_id=cs[0], score=cs[1])
            self.session.add(rec)
        self.session.commit()

    def get_info_by_id(self, user_id):
        """
        :param user_id:
        :return: info (dict, json) or None
        """
        u = self.session.query(User).get(user_id)
        if u:
            return u.info
        else:
            return None

    def add_user(self, info: dict, autocommit=True):
        u = User(id=info.get('id'), info=info)
        self.session.add(u)
        if autocommit:
            self.session.commit()

    def add_several_users(self, info: list):
        """
        Add users to database
        :param info: List of user info (dict, json)
        :return: No return
        """
        for i in info:
            self.add_user(i, autocommit=False)
        self.session.commit()

    def update_info(self, user_id, info):
        """
        Update info for particular user, create user if doesn't exist
        :param user_id: pk in User table
        :param info: info (JSON/dict format)
        :return: No return
        """
        user = self.session.query(User).get(user_id)
        if user:
            user.info = info
            self.session.commit()
        else:
            self.add_user(info)

    def add_photos(self, user_id, photos):
        """
        Add information about photo to user
        :param user_id:
        :param photos: Info about photo in dict, json.
        :return: No return
        """
        x = self.session.query(User).get(user_id)
        x.photos = photos
        self.session.commit()

    def get_photos(self, user_id):
        """
        :param user_id:
        :return: photos (dict, json) or None
        """
        x = self.session.query(User).get(user_id)
        if x:
            return x.photos
        else:
            return None

    def del_users(self):
        """
        Clean up User table
        :return: No return
        """
        self.session.query(User).delete()
        self.session.commit()

    def del_score(self):
        """
        Clean up Score table
        :return: No return
        """
        self.session.query(Score).delete()
        self.session.commit()

    def init_database(self):
        """
        Create all tables
        :return: No return
        """
        try:
            Base.metadata.create_all(self.conn.engine)
        except Exception:
            return False
        return True

    def delete_all(self):
        """
        Delete all tables
        :return: No return
        """
        self.del_score()
        self.del_users()


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


if __name__ == '__main__':
    pass
else:
    # validate connection and database and connect to vk db
    dbvk = DBVK()
    if not dbvk.check_connection():
        print('Error. Unable create connection to database. Check that Postgres ',
              'server is running and that credentials in system_settings.py are correct.')
        exit(1)
    if not dbvk.check_vk_db_exists():
        if not dbvk.create_vk_db():
            print(f'Error during creation database {dbvk.db_name_vk}')
            exit(1)
    if not dbvk.connect_to_vk_db():
        print(f'Error during connection to database {dbvk.db_name_vk}')
        exit(1)
    if not dbvk.init_database():
        print(f'Unable to create tables in {dbvk.db_name_vk} database')
        exit(1)
