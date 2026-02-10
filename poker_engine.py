import random
from enum import Enum
from collections import Counter
from typing import List, Tuple, Optional


class Suit(Enum):
    HEARTS = "♥️"
    DIAMONDS = "♦️"
    CLUBS = "♣️"
    SPADES = "♠️"


class Rank(Enum):
    TWO = (2, "2")
    THREE = (3, "3")
    FOUR = (4, "4")
    FIVE = (5, "5")
    SIX = (6, "6")
    SEVEN = (7, "7")
    EIGHT = (8, "8")
    NINE = (9, "9")
    TEN = (10, "10")
    JACK = (11, "J")
    QUEEN = (12, "Q")
    KING = (13, "K")
    ACE = (14, "A")

    def __init__(self, value, symbol):
        self.value = value
        self.symbol = symbol


class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return f"{self.rank.symbol}{self.suit.value}"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.rank.value < other.rank.value

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class HandRank(Enum):
    HIGH_CARD = (1, "Старшая карта")
    PAIR = (2, "Пара")
    TWO_PAIR = (3, "Две пары")
    THREE_OF_A_KIND = (4, "Тройка")
    STRAIGHT = (5, "Стрит")
    FLUSH = (6, "Флеш")
    FULL_HOUSE = (7, "Фулл хаус")
    FOUR_OF_A_KIND = (8, "Каре")
    STRAIGHT_FLUSH = (9, "Стрит флеш")
    ROYAL_FLUSH = (10, "Роял флеш")

    def __init__(self, value, name_ru):
        self.value = value
        self.name_ru = name_ru


class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, count: int = 1) -> List[Card]:
        if count > len(self.cards):
            raise ValueError("Not enough cards in deck")
        dealt_cards = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt_cards


class PokerHandEvaluator:
    @staticmethod
    def evaluate(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Оценивает покерную комбинацию
        Возвращает (ранг комбинации, список значений для сравнения)
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")

        sorted_cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)

        # Проверяем все возможные комбинации из 5 карт
        best_hand = None
        best_rank = HandRank.HIGH_CARD
        best_values = []

        # Если карт больше 5, проверяем все комбинации
        if len(cards) > 5:
            from itertools import combinations
            for combo in combinations(cards, 5):
                rank, values = PokerHandEvaluator._evaluate_five_cards(list(combo))
                if rank.value > best_rank.value or (rank.value == best_rank.value and values > best_values):
                    best_rank = rank
                    best_values = values
                    best_hand = list(combo)
        else:
            best_rank, best_values = PokerHandEvaluator._evaluate_five_cards(sorted_cards)
            best_hand = sorted_cards

        return best_rank, best_values, best_hand

    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """Оценка ровно 5 карт"""
        sorted_cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)

        is_flush = len(set(c.suit for c in cards)) == 1
        is_straight, straight_high = PokerHandEvaluator._check_straight(sorted_cards)

        rank_counts = Counter(c.rank.value for c in sorted_cards)
        counts = sorted(rank_counts.values(), reverse=True)

        # Роял флеш
        if is_flush and is_straight and straight_high == 14:
            return HandRank.ROYAL_FLUSH, [14]

        # Стрит флеш
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, [straight_high]

        # Каре
        if counts == [4, 1]:
            four_rank = [r for r, c in rank_counts.items() if c == 4][0]
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return HandRank.FOUR_OF_A_KIND, [four_rank, kicker]

        # Фулл хаус
        if counts == [3, 2]:
            three_rank = [r for r, c in rank_counts.items() if c == 3][0]
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            return HandRank.FULL_HOUSE, [three_rank, pair_rank]

        # Флеш
        if is_flush:
            return HandRank.FLUSH, [c.rank.value for c in sorted_cards]

        # Стрит
        if is_straight:
            return HandRank.STRAIGHT, [straight_high]

        # Тройка
        if counts == [3, 1, 1]:
            three_rank = [r for r, c in rank_counts.items() if c == 3][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return HandRank.THREE_OF_A_KIND, [three_rank] + kickers

        # Две пары
        if counts == [2, 2, 1]:
            pairs = sorted([r for r, c in rank_counts.items() if c == 2], reverse=True)
            kicker = [r for r, c in rank_counts.items() if c == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]

        # Пара
        if counts == [2, 1, 1, 1]:
            pair_rank = [r for r, c in rank_counts.items() if c == 2][0]
            kickers = sorted([r for r, c in rank_counts.items() if c == 1], reverse=True)
            return HandRank.PAIR, [pair_rank] + kickers

        # Старшая карта
        return HandRank.HIGH_CARD, [c.rank.value for c in sorted_cards]

    @staticmethod
    def _check_straight(cards: List[Card]) -> Tuple[bool, int]:
        """Проверка на стрит"""
        values = sorted([c.rank.value for c in cards], reverse=True)

        # Обычный стрит
        if values == list(range(values[0], values[0] - 5, -1)):
            return True, values[0]

        # A-2-3-4-5 стрит (колесо)
        if values == [14, 5, 4, 3, 2]:
            return True, 5

        return False, 0

    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[int]],
                     hand2: Tuple[HandRank, List[int]]) -> int:
        """
        Сравнивает две руки
        Возвращает: 1 если hand1 лучше, -1 если hand2 лучше, 0 если равны
        """
        rank1, values1 = hand1
        rank2, values2 = hand2

        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Одинаковые комбинации, сравниваем по значениям
            for v1, v2 in zip(values1, values2):
                if v1 > v2:
                    return 1
                elif v1 < v2:
                    return -1
            return 0


class Player:
    def __init__(self, user_id: int, name: str, chips: int = 1000):
        self.user_id = user_id
        self.name = name
        self.chips = chips
        self.hand: List[Card] = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False

    def bet(self, amount: int) -> int:
        """Делает ставку, возвращает реальную сумму ставки"""
        if amount >= self.chips:
            # All-in
            bet = self.chips
            self.chips = 0
            self.all_in = True
        else:
            bet = amount
            self.chips -= amount

        self.current_bet += bet
        return bet

    def fold(self):
        self.folded = True

    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False


class PokerGame:
    def __init__(self, game_id: str, small_blind: int = 10, big_blind: int = 20):
        self.game_id = game_id
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.players: List[Player] = []
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_position = 0
        self.current_player_index = 0
        self.stage = "waiting"  # waiting, preflop, flop, turn, river, showdown
        self.min_players = 2
        self.max_players = 9

    def add_player(self, user_id: int, name: str, chips: int = 1000) -> bool:
        if len(self.players) >= self.max_players:
            return False

        # Проверяем, что игрок еще не добавлен
        if any(p.user_id == user_id for p in self.players):
            return False

        player = Player(user_id, name, chips)
        self.players.append(player)
        return True

    def remove_player(self, user_id: int) -> bool:
        self.players = [p for p in self.players if p.user_id != user_id]
        return True

    def start_game(self) -> bool:
        if len(self.players) < self.min_players:
            return False

        self.stage = "preflop"
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0

        # Раздаем карты
        for player in self.players:
            player.reset_for_new_hand()
            player.hand = self.deck.deal(2)

        # Ставим блайнды
        self._post_blinds()

        # Определяем первого игрока (после big blind)
        self.current_player_index = (self.dealer_position + 3) % len(self.players)

        return True

    def _post_blinds(self):
        """Размещение блайндов"""
        sb_index = (self.dealer_position + 1) % len(self.players)
        bb_index = (self.dealer_position + 2) % len(self.players)

        sb_player = self.players[sb_index]
        bb_player = self.players[bb_index]

        # Small blind
        sb_bet = sb_player.bet(self.small_blind)
        self.pot += sb_bet

        # Big blind
        bb_bet = bb_player.bet(self.big_blind)
        self.pot += bb_bet
        self.current_bet = self.big_blind

    def get_current_player(self) -> Optional[Player]:
        if self.stage in ["waiting", "showdown"]:
            return None

        active_players = [p for p in self.players if not p.folded and not p.all_in]
        if not active_players:
            return None

        return self.players[self.current_player_index]

    def player_action(self, user_id: int, action: str, amount: int = 0) -> bool:
        """
        Обработка действия игрока
        action: fold, check, call, raise, all_in
        """
        current_player = self.get_current_player()
        if not current_player or current_player.user_id != user_id:
            return False

        if action == "fold":
            current_player.fold()
        elif action == "check":
            if current_player.current_bet < self.current_bet:
                return False  # Нельзя check если есть ставка
        elif action == "call":
            call_amount = self.current_bet - current_player.current_bet
            bet = current_player.bet(call_amount)
            self.pot += bet
        elif action == "raise":
            if amount < self.current_bet * 2:
                return False  # Минимальный рейз - удвоение текущей ставки
            total_bet = amount - current_player.current_bet
            bet = current_player.bet(total_bet)
            self.pot += bet
            self.current_bet = current_player.current_bet
        elif action == "all_in":
            bet = current_player.bet(current_player.chips)
            self.pot += bet
            if current_player.current_bet > self.current_bet:
                self.current_bet = current_player.current_bet

        # Переход к следующему игроку
        self._next_player()

        return True

    def _next_player(self):
        """Переход к следующему игроку"""
        active_players = [p for p in self.players if not p.folded and not p.all_in]

        if len(active_players) <= 1:
            # Все сфолдили или в all-in, переходим к showdown
            self._go_to_showdown()
            return

        # Проверяем, завершен ли раунд торговли
        if self._is_betting_round_complete():
            self._advance_stage()
            return

        # Следующий активный игрок
        start_index = self.current_player_index
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            player = self.players[self.current_player_index]

            if not player.folded and not player.all_in:
                break

            # Избегаем бесконечного цикла
            if self.current_player_index == start_index:
                self._advance_stage()
                break

    def _is_betting_round_complete(self) -> bool:
        """Проверка, завершен ли раунд торговли"""
        active_players = [p for p in self.players if not p.folded and not p.all_in]

        if not active_players:
            return True

        # Все активные игроки сделали одинаковую ставку
        return all(p.current_bet == self.current_bet for p in active_players)

    def _advance_stage(self):
        """Переход к следующей стадии игры"""
        # Сброс текущих ставок
        for player in self.players:
            player.current_bet = 0
        self.current_bet = 0

        if self.stage == "preflop":
            # Флоп - 3 карты
            self.community_cards.extend(self.deck.deal(3))
            self.stage = "flop"
        elif self.stage == "flop":
            # Терн - 1 карта
            self.community_cards.extend(self.deck.deal(1))
            self.stage = "turn"
        elif self.stage == "turn":
            # Ривер - 1 карта
            self.community_cards.extend(self.deck.deal(1))
            self.stage = "river"
        elif self.stage == "river":
            # Шоудаун
            self._go_to_showdown()
            return

        # Первый игрок после дилера
        self.current_player_index = (self.dealer_position + 1) % len(self.players)

    def _go_to_showdown(self):
        """Определение победителя"""
        self.stage = "showdown"

        active_players = [p for p in self.players if not p.folded]

        if len(active_players) == 1:
            # Все сфолдили, победитель автоматически
            winner = active_players[0]
            winner.chips += self.pot
            return [winner]

        # Оцениваем руки
        player_hands = []
        for player in active_players:
            all_cards = player.hand + self.community_cards
            rank, values, best_hand = PokerHandEvaluator.evaluate(all_cards)
            player_hands.append((player, rank, values, best_hand))

        # Сортируем по силе руки
        player_hands.sort(key=lambda x: (x[1].value, x[2]), reverse=True)

        # Определяем победителей (может быть несколько при равных руках)
        winners = [player_hands[0]]
        for i in range(1, len(player_hands)):
            comparison = PokerHandEvaluator.compare_hands(
                (player_hands[0][1], player_hands[0][2]),
                (player_hands[i][1], player_hands[i][2])
            )
            if comparison == 0:
                winners.append(player_hands[i])
            else:
                break

        # Делим банк между победителями
        pot_share = self.pot // len(winners)
        for winner_data in winners:
            winner_data[0].chips += pot_share

        return [w[0] for w in winners], [w[1] for w in winners], [w[3] for w in winners]

    def get_game_state(self) -> dict:
        """Возвращает текущее состояние игры"""
        return {
            "stage": self.stage,
            "pot": self.pot,
            "current_bet": self.current_bet,
            "community_cards": [str(c) for c in self.community_cards],
            "players": [
                {
                    "name": p.name,
                    "chips": p.chips,
                    "current_bet": p.current_bet,
                    "folded": p.folded,
                    "all_in": p.all_in,
                    "hand": [str(c) for c in p.hand] if self.stage == "showdown" else ["🂠", "🂠"]
                }
                for p in self.players
            ],
            "current_player": self.get_current_player().name if self.get_current_player() else None
        }
