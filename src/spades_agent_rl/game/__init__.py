"""Game engine modules."""

from .cards import Card, Rank, Suit, make_shuffled_deck, make_standard_deck
from .spades import (
    deal_hands,
    IllegalMoveError,
    RoundResult,
    RoundScores,
    SpadesRound,
    score_round,
    team_for_seat,
)

__all__ = [
    "Card",
    "deal_hands",
    "IllegalMoveError",
    "Rank",
    "RoundResult",
    "RoundScores",
    "SpadesRound",
    "Suit",
    "make_shuffled_deck",
    "make_standard_deck",
    "score_round",
    "team_for_seat",
]
