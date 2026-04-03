from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from spades_agent_rl.game.cards import Card


@dataclass(frozen=True)
class BidContext:
    seat: int
    hand: tuple[Card, ...]
    team_scores: tuple[int, int]
    dealer: int


@dataclass(frozen=True)
class PlayContext:
    seat: int
    hand: tuple[Card, ...]
    legal_cards: tuple[Card, ...]
    current_trick: tuple[tuple[int, Card], ...]
    completed_tricks: int
    spades_broken: bool
    bids: dict[int, int]
    tricks_won: tuple[int, int, int, int]


class Agent(Protocol):
    seat: int
    name: str
    is_human: bool

    def choose_bid(self, context: BidContext) -> int:
        ...

    def choose_card(self, context: PlayContext) -> Card:
        ...
