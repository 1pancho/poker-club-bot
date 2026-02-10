from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class PokerRoom(Base):
    __tablename__ = 'poker_rooms'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    creator_id = Column(Integer, nullable=False)
    creator_name = Column(String, nullable=False)
    room_name = Column(String, nullable=False)
    max_players = Column(Integer, default=9)
    buy_in = Column(String, default="Не указан")
    date_time = Column(String)
    location = Column(String, default="Не указана")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    players = relationship("Player", back_populates="room", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('poker_rooms.id'))
    user_id = Column(Integer, nullable=False)
    username = Column(String)
    full_name = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("PokerRoom", back_populates="players")


class Database:
    def __init__(self, db_url='sqlite:///poker_club.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_room(self, chat_id, creator_id, creator_name, room_name, max_players=9,
                    buy_in="Не указан", date_time=None, location="Не указана"):
        room = PokerRoom(
            chat_id=chat_id,
            creator_id=creator_id,
            creator_name=creator_name,
            room_name=room_name,
            max_players=max_players,
            buy_in=buy_in,
            date_time=date_time,
            location=location
        )
        self.session.add(room)
        self.session.commit()
        return room

    def get_active_rooms(self, chat_id):
        return self.session.query(PokerRoom).filter_by(
            chat_id=chat_id,
            is_active=True
        ).all()

    def get_room(self, room_id):
        return self.session.query(PokerRoom).filter_by(id=room_id).first()

    def add_player(self, room_id, user_id, username, full_name):
        # Проверяем, не добавлен ли игрок уже
        existing = self.session.query(Player).filter_by(
            room_id=room_id,
            user_id=user_id
        ).first()

        if existing:
            return None

        player = Player(
            room_id=room_id,
            user_id=user_id,
            username=username,
            full_name=full_name
        )
        self.session.add(player)
        self.session.commit()
        return player

    def remove_player(self, room_id, user_id):
        player = self.session.query(Player).filter_by(
            room_id=room_id,
            user_id=user_id
        ).first()

        if player:
            self.session.delete(player)
            self.session.commit()
            return True
        return False

    def close_room(self, room_id):
        room = self.get_room(room_id)
        if room:
            room.is_active = False
            self.session.commit()
            return True
        return False

    def get_room_players_count(self, room_id):
        return self.session.query(Player).filter_by(room_id=room_id).count()
