from __future__ import annotations

from dataclasses import dataclass

from spades_agent_rl.agents.base import BidContext, PlayContext
from spades_agent_rl.game import Card, Rank, Suit


SUIT_SORT_ORDER = {
    Suit.CLUBS: 0,
    Suit.DIAMONDS: 1,
    Suit.HEARTS: 2,
    Suit.SPADES: 3,
}


def _sort_cards(cards: list[Card]) -> list[Card]:
    return sorted(cards, key=lambda card: (SUIT_SORT_ORDER[card.suit], card.rank))


@dataclass
class HeuristicBot:
    seat: int
    name: str
    is_human: bool = False

    def choose_bid(self, context: BidContext) -> int:
        hand = list(context.hand)
        spades = [card for card in hand if card.suit == Suit.SPADES]
        suit_lengths = {suit: sum(1 for card in hand if card.suit == suit) for suit in Suit}
        bid_estimate = 0.0

        for card in hand:
            if card.suit == Suit.SPADES:
                if card.rank >= Rank.ACE:
                    bid_estimate += 1.0
                elif card.rank >= Rank.KING:
                    bid_estimate += 0.9
                elif card.rank >= Rank.QUEEN:
                    bid_estimate += 0.75
                elif card.rank >= Rank.JACK:
                    bid_estimate += 0.6
                elif card.rank >= Rank.TEN:
                    bid_estimate += 0.35
            elif card.rank == Rank.ACE:
                bid_estimate += 1.0
            elif card.rank == Rank.KING:
                if suit_lengths[card.suit] <= 3:
                    bid_estimate += 0.75
            elif card.rank == Rank.QUEEN:
                if suit_lengths[card.suit] <= 2:
                    bid_estimate += 0.3

        if len(spades) >= 5:
            bid_estimate += 0.75
        if len(spades) >= 7:
            bid_estimate += 0.5

        void_suits = sum(1 for suit in (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS) if suit_lengths[suit] == 0)
        singletons = sum(1 for suit in (Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS) if suit_lengths[suit] == 1)
        bid_estimate += 0.5 * void_suits
        bid_estimate += 0.2 * singletons

        bid = round(bid_estimate)

        return max(1, min(6, bid))

    def choose_card(self, context: PlayContext) -> Card:
        legal_cards = _sort_cards(list(context.legal_cards))

        if not context.current_trick:
            return _choose_lead_card(legal_cards)

        current_winner_seat, winning_card = _current_winner(context.current_trick)
        partner_seat = (context.seat + 2) % 4
        partner_winning = current_winner_seat == partner_seat
        leading_suit = context.current_trick[0][1].suit
        same_suit_cards = [card for card in legal_cards if card.suit == leading_suit]
        if same_suit_cards:
            if partner_winning:
                return same_suit_cards[0]
            better_cards = _cards_that_beat(winning_card, same_suit_cards, leading_suit)
            if better_cards:
                return better_cards[0]
            return same_suit_cards[0]

        spades = [card for card in legal_cards if card.suit == Suit.SPADES]
        if spades:
            if partner_winning:
                return _lowest_non_spade(legal_cards) or spades[0]
            better_spades = _cards_that_beat(winning_card, spades, leading_suit)
            if better_spades:
                return better_spades[0]
            return _lowest_non_spade(legal_cards) or spades[0]

        return _lowest_non_spade(legal_cards) or legal_cards[0]


def _choose_lead_card(legal_cards: list[Card]) -> Card:
    non_spades = [card for card in legal_cards if card.suit != Suit.SPADES]
    candidate_pool = non_spades or legal_cards
    suit_counts = {suit: sum(1 for card in candidate_pool if card.suit == suit) for suit in Suit}
    best_suit = min(
        {card.suit for card in candidate_pool},
        key=lambda suit: (-suit_counts[suit], SUIT_SORT_ORDER[suit]),
    )
    suited_cards = [card for card in candidate_pool if card.suit == best_suit]
    return suited_cards[0]


def _lowest_non_spade(cards: list[Card]) -> Card | None:
    non_spades = [card for card in cards if card.suit != Suit.SPADES]
    return non_spades[0] if non_spades else None


def _cards_that_beat(winning_card: Card, cards: list[Card], leading_suit: Suit) -> list[Card]:
    beating_cards: list[Card] = []
    for card in cards:
        if winning_card.suit == Suit.SPADES:
            if card.suit == Suit.SPADES and card.rank > winning_card.rank:
                beating_cards.append(card)
        elif card.suit == Suit.SPADES:
            beating_cards.append(card)
        elif card.suit == leading_suit and card.rank > winning_card.rank:
            beating_cards.append(card)
    return _sort_cards(beating_cards)


def _current_winner(current_trick: tuple[tuple[int, Card], ...]) -> tuple[int, Card]:
    leading_suit = current_trick[0][1].suit
    winning_seat, winning_card = current_trick[0]
    for seat, card in current_trick[1:]:
        if winning_card.suit == Suit.SPADES:
            if card.suit == Suit.SPADES and card.rank > winning_card.rank:
                winning_seat = seat
                winning_card = card
            continue
        if card.suit == Suit.SPADES:
            winning_seat = seat
            winning_card = card
            continue
        if card.suit == leading_suit and card.rank > winning_card.rank:
            winning_seat = seat
            winning_card = card
    return winning_seat, winning_card
