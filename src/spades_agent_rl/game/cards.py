from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum
from random import Random


class Suit(StrEnum):
    CLUBS = "Clubs"
    DIAMONDS = "Diamonds"
    HEARTS = "Hearts"
    SPADES = "Spades"


class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


RANK_LABELS: dict[Rank, str] = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "Jack",
    Rank.QUEEN: "Queen",
    Rank.KING: "King",
    Rank.ACE: "Ace",
}


@dataclass(frozen=True, order=True)
class Card:
    suit: Suit
    rank: Rank

    def __str__(self) -> str:
        return f"{RANK_LABELS[self.rank]} of {self.suit.value}"


def make_standard_deck() -> list[Card]:
    return [Card(suit=suit, rank=rank) for suit in Suit for rank in Rank]


def make_shuffled_deck(seed: int | None = None) -> list[Card]:
    deck = make_standard_deck()
    rng = Random(seed)
    rng.shuffle(deck)
    return deck
