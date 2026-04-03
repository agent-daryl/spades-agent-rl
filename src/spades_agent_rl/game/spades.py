from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card, Suit, make_shuffled_deck


class IllegalMoveError(ValueError):
    """Raised when a move violates Spades turn or card-play rules."""


def team_for_seat(seat: int) -> int:
    if seat not in (0, 1, 2, 3):
        raise ValueError(f"Seat must be 0-3, got {seat}")
    return 0 if seat % 2 == 0 else 1


def _validate_hands(hands: dict[int, list[Card]]) -> None:
    if set(hands) != {0, 1, 2, 3}:
        raise ValueError("Hands must contain seats 0, 1, 2, and 3")
    cards = [card for seat_cards in hands.values() for card in seat_cards]
    if len(cards) != 52:
        raise ValueError("A Spades round requires exactly 52 cards across all hands")
    if len(set(cards)) != 52:
        raise ValueError("Hands contain duplicate cards")
    for seat, seat_cards in hands.items():
        if len(seat_cards) != 13:
            raise ValueError(f"Seat {seat} must start with 13 cards")


@dataclass(frozen=True)
class RoundScores:
    team0_bid: int
    team1_bid: int
    team0_tricks: int
    team1_tricks: int
    team0_score_delta: int
    team1_score_delta: int
    team0_bags: int
    team1_bags: int


@dataclass(frozen=True)
class RoundResult:
    seat_tricks: tuple[int, int, int, int]
    scores: RoundScores


def deal_hands(seed: int | None = None) -> dict[int, list[Card]]:
    deck = make_shuffled_deck(seed=seed)
    hands = {seat: [] for seat in range(4)}
    for index, card in enumerate(deck):
        hands[index % 4].append(card)
    return hands


@dataclass
class SpadesRound:
    hands: dict[int, list[Card]]
    bids: dict[int, int]
    leader: int = 0
    spades_broken: bool = False
    completed_tricks: list[list[tuple[int, Card]]] = field(default_factory=list)
    current_trick: list[tuple[int, Card]] = field(default_factory=list)
    next_seat: int = field(init=False)

    def __post_init__(self) -> None:
        _validate_hands(self.hands)
        if set(self.bids) != {0, 1, 2, 3}:
            raise ValueError("Bids must be present for seats 0, 1, 2, and 3")
        if any(bid < 0 or bid > 13 for bid in self.bids.values()):
            raise ValueError("Each bid must be between 0 and 13")
        if self.leader not in (0, 1, 2, 3):
            raise ValueError("Leader must be a seat index 0-3")
        self.next_seat = self.leader
        for seat in self.hands:
            self.hands[seat] = sorted(self.hands[seat], key=lambda card: (card.suit.value, card.rank))

    @property
    def leading_suit(self) -> Suit | None:
        if not self.current_trick:
            return None
        return self.current_trick[0][1].suit

    @property
    def is_complete(self) -> bool:
        return len(self.completed_tricks) == 13

    def legal_actions(self, seat: int) -> list[Card]:
        if seat != self.next_seat:
            raise IllegalMoveError(f"It is seat {self.next_seat}'s turn, not seat {seat}")

        hand = self.hands[seat]
        if not hand:
            return []

        leading_suit = self.leading_suit
        if leading_suit is not None:
            same_suit_cards = [card for card in hand if card.suit == leading_suit]
            return same_suit_cards or list(hand)

        if self.spades_broken:
            return list(hand)

        non_spades = [card for card in hand if card.suit != Suit.SPADES]
        return non_spades or list(hand)

    def play_card(self, seat: int, card: Card) -> int | None:
        legal_cards = self.legal_actions(seat)
        if card not in legal_cards:
            raise IllegalMoveError(f"Card {card} is not legal for seat {seat}")

        self.hands[seat].remove(card)
        self.current_trick.append((seat, card))
        if card.suit == Suit.SPADES:
            self.spades_broken = True

        if len(self.current_trick) < 4:
            self.next_seat = (seat + 1) % 4
            return None

        winner = self._resolve_current_trick()
        self.completed_tricks.append(list(self.current_trick))
        self.current_trick.clear()
        self.leader = winner
        self.next_seat = winner
        return winner

    def _resolve_current_trick(self) -> int:
        leading_suit = self.leading_suit
        assert leading_suit is not None
        winning_seat, winning_card = self.current_trick[0]
        for seat, card in self.current_trick[1:]:
            if winning_card.suit == Suit.SPADES:
                if card.suit == Suit.SPADES and card.rank > winning_card.rank:
                    winning_seat, winning_card = seat, card
                continue
            if card.suit == Suit.SPADES:
                winning_seat, winning_card = seat, card
                continue
            if card.suit == leading_suit and card.rank > winning_card.rank:
                winning_seat, winning_card = seat, card
        return winning_seat

    def trick_counts_by_seat(self) -> tuple[int, int, int, int]:
        counts = [0, 0, 0, 0]
        for trick in self.completed_tricks:
            winner = self._resolve_trick_snapshot(trick)
            counts[winner] += 1
        return tuple(counts)

    def team_tricks(self) -> tuple[int, int]:
        seat_tricks = self.trick_counts_by_seat()
        return (seat_tricks[0] + seat_tricks[2], seat_tricks[1] + seat_tricks[3])

    def finish(self) -> RoundResult:
        if not self.is_complete:
            raise ValueError("Cannot finish an incomplete round")
        team0_tricks, team1_tricks = self.team_tricks()
        team0_bid = self.bids[0] + self.bids[2]
        team1_bid = self.bids[1] + self.bids[3]
        scores = score_round(team0_bid, team1_bid, team0_tricks, team1_tricks)
        return RoundResult(seat_tricks=self.trick_counts_by_seat(), scores=scores)

    @staticmethod
    def _resolve_trick_snapshot(trick: list[tuple[int, Card]]) -> int:
        leading_suit = trick[0][1].suit
        winning_seat, winning_card = trick[0]
        for seat, card in trick[1:]:
            if winning_card.suit == Suit.SPADES:
                if card.suit == Suit.SPADES and card.rank > winning_card.rank:
                    winning_seat, winning_card = seat, card
                continue
            if card.suit == Suit.SPADES:
                winning_seat, winning_card = seat, card
                continue
            if card.suit == leading_suit and card.rank > winning_card.rank:
                winning_seat, winning_card = seat, card
        return winning_seat


def score_round(team0_bid: int, team1_bid: int, team0_tricks: int, team1_tricks: int) -> RoundScores:
    team0_score_delta, team0_bags = _score_team(team0_bid, team0_tricks)
    team1_score_delta, team1_bags = _score_team(team1_bid, team1_tricks)
    return RoundScores(
        team0_bid=team0_bid,
        team1_bid=team1_bid,
        team0_tricks=team0_tricks,
        team1_tricks=team1_tricks,
        team0_score_delta=team0_score_delta,
        team1_score_delta=team1_score_delta,
        team0_bags=team0_bags,
        team1_bags=team1_bags,
    )


def _score_team(bid: int, tricks: int) -> tuple[int, int]:
    if bid < 0 or bid > 13:
        raise ValueError("Team bid must be between 0 and 13")
    if tricks < 0 or tricks > 13:
        raise ValueError("Team tricks must be between 0 and 13")

    if tricks < bid:
        return (-10 * bid, 0)
    bags = tricks - bid
    return (10 * bid + bags, bags)
