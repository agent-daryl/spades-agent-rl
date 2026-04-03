from __future__ import annotations

import unittest

from spades_agent_rl.agents import HeuristicBot
from spades_agent_rl.agents.base import BidContext, PlayContext
from spades_agent_rl.game import Card, Rank, Suit


class HeuristicBotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = HeuristicBot(seat=0, name="North")

    def test_bid_increases_with_strong_spade_hand(self) -> None:
        strong_hand = (
            Card(Suit.SPADES, Rank.ACE),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.SPADES, Rank.TEN),
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.TWO),
            Card(Suit.HEARTS, Rank.THREE),
            Card(Suit.DIAMONDS, Rank.TWO),
            Card(Suit.DIAMONDS, Rank.THREE),
        )
        weak_hand = (
            Card(Suit.CLUBS, Rank.TWO),
            Card(Suit.CLUBS, Rank.THREE),
            Card(Suit.CLUBS, Rank.FOUR),
            Card(Suit.DIAMONDS, Rank.TWO),
            Card(Suit.DIAMONDS, Rank.THREE),
            Card(Suit.DIAMONDS, Rank.FOUR),
            Card(Suit.HEARTS, Rank.TWO),
            Card(Suit.HEARTS, Rank.THREE),
            Card(Suit.HEARTS, Rank.FOUR),
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.SPADES, Rank.THREE),
            Card(Suit.SPADES, Rank.FOUR),
            Card(Suit.SPADES, Rank.FIVE),
        )

        strong_bid = self.bot.choose_bid(BidContext(seat=0, hand=strong_hand, team_scores=(0, 0), dealer=3))
        weak_bid = self.bot.choose_bid(BidContext(seat=0, hand=weak_hand, team_scores=(0, 0), dealer=3))
        self.assertGreater(strong_bid, weak_bid)

    def test_does_not_overtake_partner_when_partner_is_winning(self) -> None:
        chosen = self.bot.choose_card(
            PlayContext(
                seat=0,
                hand=(
                    Card(Suit.HEARTS, Rank.FIVE),
                    Card(Suit.HEARTS, Rank.KING),
                ),
                legal_cards=(
                    Card(Suit.HEARTS, Rank.FIVE),
                    Card(Suit.HEARTS, Rank.KING),
                ),
                current_trick=(
                    (1, Card(Suit.HEARTS, Rank.TEN)),
                    (2, Card(Suit.HEARTS, Rank.ACE)),
                ),
                completed_tricks=3,
                spades_broken=False,
                bids={0: 3, 1: 2, 2: 3, 3: 2},
                tricks_won=(1, 1, 1, 0),
            )
        )
        self.assertEqual(chosen, Card(Suit.HEARTS, Rank.FIVE))

    def test_uses_lowest_winning_spade_when_void(self) -> None:
        chosen = self.bot.choose_card(
            PlayContext(
                seat=0,
                hand=(
                    Card(Suit.SPADES, Rank.FOUR),
                    Card(Suit.SPADES, Rank.KING),
                    Card(Suit.CLUBS, Rank.TWO),
                ),
                legal_cards=(
                    Card(Suit.SPADES, Rank.FOUR),
                    Card(Suit.SPADES, Rank.KING),
                    Card(Suit.CLUBS, Rank.TWO),
                ),
                current_trick=(
                    (1, Card(Suit.HEARTS, Rank.QUEEN)),
                    (2, Card(Suit.HEARTS, Rank.THREE)),
                ),
                completed_tricks=5,
                spades_broken=True,
                bids={0: 3, 1: 2, 2: 3, 3: 2},
                tricks_won=(1, 2, 1, 1),
            )
        )
        self.assertEqual(chosen, Card(Suit.SPADES, Rank.FOUR))
