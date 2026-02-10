from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class PlayerProfile(Base):
    """Профиль игрока с балансом и статистикой"""
    __tablename__ = 'player_profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    full_name = Column(String, nullable=False)
    chips = Column(Integer, default=1000)  # Виртуальные фишки
    total_games = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    total_winnings = Column(Integer, default=0)
    rating = Column(Integer, default=1000)  # ELO рейтинг
    created_at = Column(DateTime, default=datetime.utcnow)
    last_daily_bonus = Column(DateTime)

    game_participations = relationship("GameParticipation", back_populates="player")
    tournament_participations = relationship("TournamentParticipation", back_populates="player")


class GameTable(Base):
    """Игровой стол (активная игра)"""
    __tablename__ = 'game_tables'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    message_id = Column(Integer)  # ID сообщения с игрой
    creator_id = Column(Integer, nullable=False)
    small_blind = Column(Integer, default=10)
    big_blind = Column(Integer, default=20)
    min_buy_in = Column(Integer, default=100)
    max_buy_in = Column(Integer, default=10000)
    max_players = Column(Integer, default=9)
    status = Column(String, default="waiting")  # waiting, playing, finished
    current_stage = Column(String)  # preflop, flop, turn, river, showdown
    pot = Column(Integer, default=0)
    community_cards = Column(JSON)  # Список общих карт
    game_state = Column(JSON)  # Полное состояние игры
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    participations = relationship("GameParticipation", back_populates="table")


class GameParticipation(Base):
    """Участие игрока в игре"""
    __tablename__ = 'game_participations'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('game_tables.id'))
    player_id = Column(Integer, ForeignKey('player_profiles.id'))
    buy_in = Column(Integer, nullable=False)
    current_chips = Column(Integer)
    position = Column(Integer)  # Позиция за столом
    is_active = Column(Boolean, default=True)
    folded = Column(Boolean, default=False)
    winnings = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)

    table = relationship("GameTable", back_populates="participations")
    player = relationship("PlayerProfile", back_populates="game_participations")


class Tournament(Base):
    """Турнир"""
    __tablename__ = 'tournaments'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    creator_id = Column(Integer, nullable=False)
    buy_in = Column(Integer, default=100)
    starting_chips = Column(Integer, default=1000)
    max_players = Column(Integer, default=18)
    prize_pool = Column(Integer, default=0)
    status = Column(String, default="registration")  # registration, running, finished
    blind_increase_minutes = Column(Integer, default=10)
    current_level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)

    participations = relationship("TournamentParticipation", back_populates="tournament")


class TournamentParticipation(Base):
    """Участие в турнире"""
    __tablename__ = 'tournament_participations'

    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'))
    player_id = Column(Integer, ForeignKey('player_profiles.id'))
    chips = Column(Integer)
    position = Column(Integer)  # Итоговое место
    prize = Column(Integer, default=0)
    is_eliminated = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    eliminated_at = Column(DateTime)

    tournament = relationship("Tournament", back_populates="participations")
    player = relationship("PlayerProfile", back_populates="tournament_participations")


class GameHistory(Base):
    """История завершенных игр"""
    __tablename__ = 'game_history'

    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('game_tables.id'))
    winner_id = Column(Integer, ForeignKey('player_profiles.id'))
    pot_size = Column(Integer)
    players_count = Column(Integer)
    duration_minutes = Column(Integer)
    finished_at = Column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self, db_url='sqlite:///poker_game.db'):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # ========== Профили игроков ==========

    def get_or_create_player(self, user_id, username, full_name):
        """Получить или создать профиль игрока"""
        player = self.session.query(PlayerProfile).filter_by(user_id=user_id).first()

        if not player:
            player = PlayerProfile(
                user_id=user_id,
                username=username,
                full_name=full_name,
                chips=1000  # Начальные фишки
            )
            self.session.add(player)
            self.session.commit()

        return player

    def update_player_chips(self, user_id, chips):
        """Обновить количество фишек игрока"""
        player = self.session.query(PlayerProfile).filter_by(user_id=user_id).first()
        if player:
            player.chips = chips
            self.session.commit()
            return True
        return False

    def add_chips(self, user_id, amount):
        """Добавить фишки игроку"""
        player = self.session.query(PlayerProfile).filter_by(user_id=user_id).first()
        if player:
            player.chips += amount
            self.session.commit()
            return player.chips
        return None

    def get_daily_bonus(self, user_id):
        """Получить ежедневный бонус"""
        player = self.session.query(PlayerProfile).filter_by(user_id=user_id).first()
        if not player:
            return None

        now = datetime.utcnow()
        if player.last_daily_bonus:
            hours_since_last = (now - player.last_daily_bonus).total_seconds() / 3600
            if hours_since_last < 24:
                return None  # Бонус уже получен сегодня

        bonus = 100
        player.chips += bonus
        player.last_daily_bonus = now
        self.session.commit()
        return bonus

    def get_leaderboard(self, limit=10):
        """Получить таблицу лидеров"""
        return self.session.query(PlayerProfile).order_by(
            PlayerProfile.rating.desc()
        ).limit(limit).all()

    # ========== Игровые столы ==========

    def create_table(self, chat_id, creator_id, small_blind=10, big_blind=20,
                    min_buy_in=100, max_buy_in=10000, max_players=9):
        """Создать новый игровой стол"""
        table = GameTable(
            chat_id=chat_id,
            creator_id=creator_id,
            small_blind=small_blind,
            big_blind=big_blind,
            min_buy_in=min_buy_in,
            max_buy_in=max_buy_in,
            max_players=max_players,
            status="waiting"
        )
        self.session.add(table)
        self.session.commit()
        return table

    def get_table(self, table_id):
        """Получить стол по ID"""
        return self.session.query(GameTable).filter_by(id=table_id).first()

    def get_active_tables(self, chat_id):
        """Получить активные столы в чате"""
        return self.session.query(GameTable).filter_by(
            chat_id=chat_id,
            status__in=["waiting", "playing"]
        ).all()

    def update_table_state(self, table_id, game_state):
        """Обновить состояние игры"""
        table = self.get_table(table_id)
        if table:
            table.game_state = game_state
            table.current_stage = game_state.get("stage")
            table.pot = game_state.get("pot", 0)
            table.community_cards = game_state.get("community_cards", [])
            self.session.commit()
            return True
        return False

    def finish_table(self, table_id):
        """Завершить игру"""
        table = self.get_table(table_id)
        if table:
            table.status = "finished"
            table.finished_at = datetime.utcnow()
            self.session.commit()
            return True
        return False

    # ========== Участие в играх ==========

    def join_table(self, table_id, player_id, buy_in):
        """Присоединиться к столу"""
        # Проверяем, что игрок еще не за столом
        existing = self.session.query(GameParticipation).filter_by(
            table_id=table_id,
            player_id=player_id,
            is_active=True
        ).first()

        if existing:
            return None

        # Проверяем, что у игрока достаточно фишек
        player = self.session.query(PlayerProfile).filter_by(id=player_id).first()
        if not player or player.chips < buy_in:
            return None

        # Списываем фишки
        player.chips -= buy_in

        # Создаем участие
        participation = GameParticipation(
            table_id=table_id,
            player_id=player_id,
            buy_in=buy_in,
            current_chips=buy_in
        )
        self.session.add(participation)
        self.session.commit()

        return participation

    def leave_table(self, table_id, player_id):
        """Покинуть стол"""
        participation = self.session.query(GameParticipation).filter_by(
            table_id=table_id,
            player_id=player_id,
            is_active=True
        ).first()

        if participation:
            # Возвращаем оставшиеся фишки
            player = self.session.query(PlayerProfile).filter_by(id=player_id).first()
            if player:
                player.chips += participation.current_chips

            participation.is_active = False
            self.session.commit()
            return True
        return False

    def get_table_players(self, table_id):
        """Получить игроков за столом"""
        participations = self.session.query(GameParticipation).filter_by(
            table_id=table_id,
            is_active=True
        ).all()

        players = []
        for p in participations:
            player = self.session.query(PlayerProfile).filter_by(id=p.player_id).first()
            if player:
                players.append({
                    "user_id": player.user_id,
                    "name": player.full_name,
                    "chips": p.current_chips,
                    "buy_in": p.buy_in
                })

        return players

    # ========== Статистика ==========

    def update_player_stats(self, user_id, won=False, winnings=0):
        """Обновить статистику игрока"""
        player = self.session.query(PlayerProfile).filter_by(user_id=user_id).first()
        if player:
            player.total_games += 1
            if won:
                player.games_won += 1
                player.total_winnings += winnings
                # Увеличиваем рейтинг за победу
                player.rating += 10
            else:
                # Немного уменьшаем рейтинг за поражение
                player.rating = max(0, player.rating - 5)

            self.session.commit()
            return True
        return False

    # ========== Турниры ==========

    def create_tournament(self, chat_id, creator_id, name, buy_in=100,
                         starting_chips=1000, max_players=18):
        """Создать турнир"""
        tournament = Tournament(
            chat_id=chat_id,
            creator_id=creator_id,
            name=name,
            buy_in=buy_in,
            starting_chips=starting_chips,
            max_players=max_players
        )
        self.session.add(tournament)
        self.session.commit()
        return tournament

    def get_tournament(self, tournament_id):
        """Получить турнир"""
        return self.session.query(Tournament).filter_by(id=tournament_id).first()

    def join_tournament(self, tournament_id, player_id):
        """Присоединиться к турниру"""
        tournament = self.get_tournament(tournament_id)
        if not tournament or tournament.status != "registration":
            return None

        # Проверяем, что игрок еще не зарегистрирован
        existing = self.session.query(TournamentParticipation).filter_by(
            tournament_id=tournament_id,
            player_id=player_id
        ).first()

        if existing:
            return None

        # Проверяем фишки игрока
        player = self.session.query(PlayerProfile).filter_by(id=player_id).first()
        if not player or player.chips < tournament.buy_in:
            return None

        # Списываем бай-ин
        player.chips -= tournament.buy_in
        tournament.prize_pool += tournament.buy_in

        # Регистрируем участие
        participation = TournamentParticipation(
            tournament_id=tournament_id,
            player_id=player_id,
            chips=tournament.starting_chips
        )
        self.session.add(participation)
        self.session.commit()

        return participation
