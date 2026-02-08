#!/usr/bin/env python3
"""Simple Tiến Lên Miền Nam console game (basic rules)."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

RANKS = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
SUITS = ["♣", "♦", "♥", "♠"]

RANK_VALUE = {rank: i for i, rank in enumerate(RANKS)}


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"

    @property
    def value(self) -> int:
        return RANK_VALUE[self.rank]


class Deck:
    def __init__(self) -> None:
        self.cards = [Card(rank, suit) for rank in RANKS for suit in SUITS]
        random.shuffle(self.cards)

    def deal(self, players: int) -> List[List[Card]]:
        hands = [[] for _ in range(players)]
        for i, card in enumerate(self.cards):
            hands[i % players].append(card)
        for hand in hands:
            hand.sort(key=lambda c: (c.value, c.suit))
        return hands


Combo = Tuple[str, List[Card]]  # (type, cards)


def parse_cards(input_str: str, hand: List[Card]) -> Optional[List[Card]]:
    tokens = input_str.strip().split()
    if not tokens:
        return None
    selected: List[Card] = []
    for token in tokens:
        found = next((c for c in hand if str(c) == token), None)
        if not found:
            return None
        selected.append(found)
    return selected


def classify_combo(cards: List[Card]) -> Optional[Combo]:
    if not cards:
        return None
    cards = sorted(cards, key=lambda c: (c.value, c.suit))
    values = [c.value for c in cards]
    unique_values = sorted(set(values))
    counts = {v: values.count(v) for v in unique_values}

    if len(cards) == 1:
        return ("single", cards)
    if len(cards) == 2 and len(unique_values) == 1:
        return ("pair", cards)
    if len(cards) == 3 and len(unique_values) == 1:
        return ("triple", cards)
    if len(cards) == 4 and len(unique_values) == 1:
        return ("four", cards)

    # straight: length >= 3, consecutive values, no 2s
    if len(cards) >= 3 and len(unique_values) == len(cards):
        if max(values) == RANK_VALUE["2"]:
            return None
        if sorted(values) == list(range(min(values), max(values) + 1)):
            return ("straight", cards)

    return None


def combo_strength(combo: Combo) -> Tuple[int, int]:
    combo_type, cards = combo
    order = {
        "single": 1,
        "pair": 2,
        "triple": 3,
        "straight": 4,
        "four": 5,
    }
    highest = max(c.value for c in cards)
    return (order[combo_type], highest)


def can_beat(current: Combo, new: Combo) -> bool:
    if current[0] != new[0]:
        return False
    if current[0] == "straight" and len(current[1]) != len(new[1]):
        return False
    return combo_strength(new) > combo_strength(current)


def bot_move(hand: List[Card], current: Optional[Combo]) -> Optional[Combo]:
    # naive bot: play the smallest legal combo
    possible: List[Combo] = []
    for i in range(len(hand)):
        for j in range(i + 1, len(hand) + 1):
            cards = hand[i:j]
            combo = classify_combo(cards)
            if not combo:
                continue
            if current is None or can_beat(current, combo):
                possible.append(combo)
    if not possible:
        return None
    possible.sort(key=combo_strength)
    return possible[0]


def remove_cards(hand: List[Card], cards: List[Card]) -> None:
    for card in cards:
        hand.remove(card)


def print_hand(hand: List[Card]) -> None:
    print(" ".join(str(card) for card in hand))


def main() -> None:
    print("=== TIẾN LÊN MIỀN NAM (BASIC) ===")
    deck = Deck()
    hands = deck.deal(4)
    current: Optional[Combo] = None
    current_player = 0
    passes = 0

    while True:
        hand = hands[current_player]
        if not hand:
            print(f"Player {current_player + 1} wins!")
            break

        print("\n--------------------------------")
        print(f"Player {current_player + 1}'s turn")

        if current_player == 0:
            print("Your hand:")
            print_hand(hand)
            if current:
                print(f"Current combo: {current[0]} -> {' '.join(str(c) for c in current[1])}")
            move = input("Play cards (space-separated) or 'pass': ").strip()
            if move.lower() == "pass":
                passes += 1
            else:
                selected = parse_cards(move, hand)
                combo = classify_combo(selected or [])
                if not combo:
                    print("Invalid combo.")
                    continue
                if current and not can_beat(current, combo):
                    print("Cannot beat current combo.")
                    continue
                remove_cards(hand, combo[1])
                current = combo
                passes = 0
        else:
            combo = bot_move(hand, current)
            if combo is None:
                print("Bot passes.")
                passes += 1
            else:
                remove_cards(hand, combo[1])
                current = combo
                passes = 0
                print(f"Bot plays: {' '.join(str(c) for c in combo[1])}")

        if passes >= 3:
            print("All others passed. Resetting round.")
            current = None
            passes = 0

        current_player = (current_player + 1) % 4


if __name__ == "__main__":
    main()
