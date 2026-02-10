#!/usr/bin/env python3
"""Simplified Tiến Lên Miền Nam game engine and CLI demo."""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import Iterable, List, Optional


RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
SUITS = ["♠", "♣", "♦", "♥"]
RANK_VALUE = {rank: index for index, rank in enumerate(RANKS)}
SUIT_VALUE = {suit: index for index, suit in enumerate(SUITS)}


@dataclass(frozen=True, order=True)
class Card:
    rank: str
    suit: str

    def __post_init__(self) -> None:
        if self.rank not in RANK_VALUE:
            raise ValueError(f"Invalid rank: {self.rank}")
        if self.suit not in SUIT_VALUE:
            raise ValueError(f"Invalid suit: {self.suit}")

    @property
    def rank_value(self) -> int:
        return RANK_VALUE[self.rank]

    @property
    def suit_value(self) -> int:
        return SUIT_VALUE[self.suit]

    def short(self) -> str:
        return f"{self.rank}{self.suit}"


@dataclass
class Combo:
    combo_type: str
    cards: List[Card]
    main_rank: int
    length: int


def create_deck() -> List[Card]:
    return [Card(rank, suit) for rank in RANKS for suit in SUITS]


def sort_cards(cards: Iterable[Card]) -> List[Card]:
    return sorted(cards, key=lambda c: (c.rank_value, c.suit_value))


def group_by_rank(cards: Iterable[Card]) -> dict[int, List[Card]]:
    grouped: dict[int, List[Card]] = {}
    for card in cards:
        grouped.setdefault(card.rank_value, []).append(card)
    return grouped


def is_straight(ranks: List[int]) -> bool:
    if len(ranks) < 3:
        return False
    if ranks[-1] == RANK_VALUE["2"]:
        return False
    return all(ranks[i + 1] - ranks[i] == 1 for i in range(len(ranks) - 1))


def is_double_straight(cards: List[Card]) -> Optional[Combo]:
    if len(cards) < 6 or len(cards) % 2 != 0:
        return None
    grouped = group_by_rank(cards)
    if any(len(grouped[rank]) != 2 for rank in grouped):
        return None
    ranks = sorted(grouped.keys())
    if not is_straight(ranks):
        return None
    return Combo("double_straight", sort_cards(cards), ranks[-1], len(ranks))


def detect_combo(cards: List[Card]) -> Optional[Combo]:
    cards = sort_cards(cards)
    if not cards:
        return None
    grouped = group_by_rank(cards)
    ranks = sorted(grouped.keys())

    if len(cards) == 1:
        return Combo("single", cards, cards[0].rank_value, 1)

    if len(cards) == 2 and len(grouped) == 1:
        return Combo("pair", cards, ranks[0], 2)

    if len(cards) == 3:
        if len(grouped) == 1:
            return Combo("triple", cards, ranks[0], 3)
        if len(grouped) == 3 and is_straight(ranks):
            return Combo("straight", cards, ranks[-1], 3)

    if len(grouped) == 1 and len(cards) == 4:
        return Combo("four_of_kind", cards, ranks[0], 4)

    if len(grouped) == len(cards) and is_straight(ranks):
        return Combo("straight", cards, ranks[-1], len(cards))

    double_straight = is_double_straight(cards)
    if double_straight:
        return double_straight

    return None


def is_bomb(combo: Combo) -> bool:
    return combo.combo_type in {"four_of_kind", "double_straight"}


def can_beat(current: Optional[Combo], challenger: Combo) -> bool:
    if current is None:
        return True

    if challenger.combo_type == current.combo_type:
        if challenger.combo_type in {"straight", "double_straight"}:
            if challenger.length != current.length:
                return False
        return challenger.main_rank > current.main_rank

    if is_bomb(challenger) and current.main_rank == RANK_VALUE["2"]:
        return True

    return False


def find_valid_moves(hand: List[Card], current: Optional[Combo]) -> List[List[Card]]:
    moves: List[List[Card]] = []
    sorted_hand = sort_cards(hand)

    for card in sorted_hand:
        combo = detect_combo([card])
        if combo and can_beat(current, combo):
            moves.append([card])

    grouped = group_by_rank(sorted_hand)
    for cards in grouped.values():
        if len(cards) >= 2:
            combo = detect_combo(cards[:2])
            if combo and can_beat(current, combo):
                moves.append(cards[:2])
        if len(cards) >= 3:
            combo = detect_combo(cards[:3])
            if combo and can_beat(current, combo):
                moves.append(cards[:3])
        if len(cards) == 4:
            combo = detect_combo(cards)
            if combo and can_beat(current, combo):
                moves.append(cards)

    ranks = sorted(set(card.rank_value for card in sorted_hand))
    for length in range(3, len(ranks) + 1):
        for start in range(len(ranks) - length + 1):
            seq = ranks[start : start + length]
            if not is_straight(seq):
                continue
            cards_seq = [min(grouped[rank], key=lambda c: c.suit_value) for rank in seq]
            combo = detect_combo(cards_seq)
            if combo and can_beat(current, combo):
                moves.append(cards_seq)

    pairs_by_rank = {rank: cards for rank, cards in grouped.items() if len(cards) >= 2}
    ranks_pairs = sorted(pairs_by_rank.keys())
    for length in range(3, len(ranks_pairs) + 1):
        for start in range(len(ranks_pairs) - length + 1):
            seq = ranks_pairs[start : start + length]
            if not is_straight(seq):
                continue
            cards_seq = []
            for rank in seq:
                cards_seq.extend(sort_cards(pairs_by_rank[rank])[:2])
            combo = detect_combo(cards_seq)
            if combo and can_beat(current, combo):
                moves.append(cards_seq)

    return moves


class Player:
    def __init__(self, name: str, is_human: bool = False) -> None:
        self.name = name
        self.is_human = is_human
        self.hand: List[Card] = []

    def sort_hand(self) -> None:
        self.hand = sort_cards(self.hand)

    def remove_cards(self, cards: List[Card]) -> None:
        for card in cards:
            self.hand.remove(card)


class TienLenGame:
    def __init__(self, players: List[Player]) -> None:
        self.players = players
        self.current_combo: Optional[Combo] = None
        self.pass_count = 0
        self.current_index = 0

    def deal(self) -> None:
        deck = create_deck()
        random.shuffle(deck)
        for index, card in enumerate(deck):
            self.players[index % len(self.players)].hand.append(card)
        for player in self.players:
            player.sort_hand()

    def find_start_player(self) -> int:
        lowest = Card("3", "♠")
        for index, player in enumerate(self.players):
            if lowest in player.hand:
                return index
        return 0

    def play_round(self) -> Player:
        self.deal()
        self.current_index = self.find_start_player()
        print(f"Người bắt đầu: {self.players[self.current_index].name}")

        while True:
            player = self.players[self.current_index]
            print(f"\nLượt của {player.name}. Bài còn lại: {len(player.hand)}")
            if player.is_human:
                cards = self.prompt_human_move(player)
            else:
                cards = self.choose_bot_move(player)

            if cards:
                combo = detect_combo(cards)
                if not combo or not can_beat(self.current_combo, combo):
                    print("Nước đi không hợp lệ, bỏ lượt.")
                    self.pass_count += 1
                else:
                    player.remove_cards(cards)
                    self.current_combo = combo
                    self.pass_count = 0
                    print(f"{player.name} đánh: {self.format_cards(cards)}")
                    if not player.hand:
                        return player
            else:
                print(f"{player.name} bỏ lượt.")
                self.pass_count += 1

            if self.pass_count >= len(self.players) - 1:
                self.current_combo = None
                self.pass_count = 0
                print("Tất cả đều bỏ lượt. Vòng mới!")

            self.current_index = (self.current_index + 1) % len(self.players)

    def choose_bot_move(self, player: Player) -> List[Card]:
        moves = find_valid_moves(player.hand, self.current_combo)
        if not moves:
            return []
        return moves[0]

    def prompt_human_move(self, player: Player) -> List[Card]:
        print("Bài trên tay:", self.format_cards(player.hand))
        raw = input("Nhập bài muốn đánh (vd: 3♠ 4♠ 5♠) hoặc Enter để bỏ: ").strip()
        if not raw:
            return []
        try:
            cards = [parse_card(token) for token in raw.split()]
        except ValueError as exc:
            print(f"Lỗi: {exc}")
            return []
        if any(card not in player.hand for card in cards):
            print("Bạn không có các lá này.")
            return []
        return cards

    @staticmethod
    def format_cards(cards: List[Card]) -> str:
        return " ".join(card.short() for card in sort_cards(cards))


def parse_card(token: str) -> Card:
    for suit in SUITS:
        if token.endswith(suit):
            rank = token[: -len(suit)]
            return Card(rank, suit)
    raise ValueError("Không nhận diện được lá bài.")


def build_players(human: bool) -> List[Player]:
    players = [
        Player("Bạn", is_human=human),
        Player("Bot 1"),
        Player("Bot 2"),
        Player("Bot 3"),
    ]
    if not human:
        players = [Player(f"Bot {index + 1}") for index in range(4)]
    return players


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiến Lên Miền Nam (phiên bản đơn giản)")
    parser.add_argument("--human", action="store_true", help="Cho phép người chơi tham gia")
    args = parser.parse_args()

    game = TienLenGame(build_players(args.human))
    winner = game.play_round()
    print(f"\nKết thúc! Người thắng là {winner.name}.")


if __name__ == "__main__":
    main()
