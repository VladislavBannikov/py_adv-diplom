from sqlalchemy import create_engine, Integer, Column, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('postgresql://netology_user:1@localhost/vk')
Session = sessionmaker(bind=engine)
session = Session()


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
    users = session.query(User).all()
    return [u.id for u in users]


def add_score(user_id: Integer, cand_score: list):
    """
    Add scores to database
    :param user_id: lonely user id
    :param cand_score: candidates with score related to lonely user (list of [candidate id, score])
    :return: no return
    """
    for cs in cand_score:
        rec = Score(user_id=user_id, candidate_id=cs[0], score=cs[1])
        session.add(rec)
    session.commit()


def get_info_by_id(user_id):
    """
    :param user_id:
    :return: info (dict, json) or None
    """
    u = session.query(User).get(user_id)
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
        session.add(u)
    session.commit()


def add_photos(user_id, photos):
    """
    Add information about photo to user
    :param user_id:
    :param photos: Info about photo in dict, json.
    :return: No return
    """
    x = session.query(User).get(user_id)
    x.photos = photos
    session.commit()


def get_photos(user_id):
    """
    :param user_id:
    :return: photos (dict, json) or None
    """
    x = session.query(User).get(user_id)
    if x:
        return x.photos
    else:
        return None


def del_users():
    """
    Clean up User table
    :return: No return
    """
    session.query(User).delete()
    session.commit()


def del_score():
    """
    Clean up Score table
    :return: No return
    """
    session.query(Score).delete()
    session.commit()


def init_database():
    """
    Create all tables
    :return: No return
    """
    Base.metadata.create_all(engine)


def delete_all():
    """
    Delete all tables
    :return: No return
    """
    Base.metadata.drop_all(engine)


if __name__ == '__main__':
    pass




