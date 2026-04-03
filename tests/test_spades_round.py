from __future__ import annotations

import unittest

from spades_agent_rl.game import Card, IllegalMoveError, Rank, SpadesRound, Suit, score_round


def make_test_hands() -> dict[int, list[Card]]:
    return {
        0: [
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.HEARTS, Rank.KING),
            Card(Suit.HEARTS, Rank.QUEEN),
            Card(Suit.HEARTS, Rank.JACK),
            Card(Suit.HEARTS, Rank.TEN),
            Card(Suit.CLUBS, Rank.TWO),
            Card(Suit.CLUBS, Rank.THREE),
            Card(Suit.CLUBS, Rank.FOUR),
            Card(Suit.DIAMONDS, Rank.TWO),
            Card(Suit.DIAMONDS, Rank.THREE),
            Card(Suit.SPADES, Rank.TWO),
            Card(Suit.SPADES, Rank.THREE),
            Card(Suit.SPADES, Rank.FOUR),
        ],
        1: [
            Card(Suit.HEARTS, Rank.TWO),
            Card(Suit.HEARTS, Rank.THREE),
            Card(Suit.HEARTS, Rank.FOUR),
            Card(Suit.HEARTS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.FIVE),
            Card(Suit.CLUBS, Rank.SIX),
            Card(Suit.CLUBS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.FOUR),
            Card(Suit.DIAMONDS, Rank.FIVE),
            Card(Suit.DIAMONDS, Rank.SIX),
            Card(Suit.SPADES, Rank.FIVE),
            Card(Suit.SPADES, Rank.SIX),
            Card(Suit.SPADES, Rank.SEVEN),
        ],
        2: [
            Card(Suit.HEARTS, Rank.SIX),
            Card(Suit.HEARTS, Rank.SEVEN),
            Card(Suit.HEARTS, Rank.EIGHT),
            Card(Suit.HEARTS, Rank.NINE),
            Card(Suit.CLUBS, Rank.EIGHT),
            Card(Suit.CLUBS, Rank.NINE),
            Card(Suit.CLUBS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.SEVEN),
            Card(Suit.DIAMONDS, Rank.EIGHT),
            Card(Suit.DIAMONDS, Rank.NINE),
            Card(Suit.SPADES, Rank.EIGHT),
            Card(Suit.SPADES, Rank.NINE),
            Card(Suit.SPADES, Rank.TEN),
        ],
        3: [
            Card(Suit.CLUBS, Rank.JACK),
            Card(Suit.CLUBS, Rank.QUEEN),
            Card(Suit.CLUBS, Rank.KING),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.TEN),
            Card(Suit.DIAMONDS, Rank.JACK),
            Card(Suit.DIAMONDS, Rank.QUEEN),
            Card(Suit.DIAMONDS, Rank.KING),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.SPADES, Rank.JACK),
            Card(Suit.SPADES, Rank.QUEEN),
            Card(Suit.SPADES, Rank.KING),
            Card(Suit.SPADES, Rank.ACE),
        ],
    }


class SpadesRoundTests(unittest.TestCase):
    def test_first_lead_cannot_break_spades_if_non_spade_exists(self) -> None:
        round_state = SpadesRound(hands=make_test_hands(), bids={0: 3, 1: 3, 2: 3, 3: 4})
        legal_cards = round_state.legal_actions(0)
        self.assertTrue(all(card.suit != Suit.SPADES for card in legal_cards))

    def test_must_follow_suit_when_possible(self) -> None:
        round_state = SpadesRound(hands=make_test_hands(), bids={0: 3, 1: 3, 2: 3, 3: 4})
        round_state.play_card(0, Card(Suit.HEARTS, Rank.ACE))
        legal_cards = round_state.legal_actions(1)
        self.assertEqual({card.suit for card in legal_cards}, {Suit.HEARTS})
        with self.assertRaises(IllegalMoveError):
            round_state.play_card(1, Card(Suit.SPADES, Rank.SIX))

    def test_spade_trumps_non_spade(self) -> None:
        round_state = SpadesRound(hands=make_test_hands(), bids={0: 3, 1: 3, 2: 3, 3: 4})
        round_state.play_card(0, Card(Suit.HEARTS, Rank.ACE))
        round_state.play_card(1, Card(Suit.HEARTS, Rank.TWO))
        round_state.play_card(2, Card(Suit.HEARTS, Rank.SIX))
        winner = round_state.play_card(3, Card(Suit.SPADES, Rank.ACE))
        self.assertEqual(winner, 3)
        self.assertTrue(round_state.spades_broken)
        self.assertEqual(round_state.next_seat, 3)

    def test_round_score_computes_bid_and_bags(self) -> None:
        scores = score_round(team0_bid=7, team1_bid=5, team0_tricks=8, team1_tricks=5)
        self.assertEqual(scores.team0_score_delta, 71)
        self.assertEqual(scores.team0_bags, 1)
        self.assertEqual(scores.team1_score_delta, 50)
        self.assertEqual(scores.team1_bags, 0)

    def test_round_finish_reports_team_tricks(self) -> None:
        round_state = SpadesRound(hands=make_test_hands(), bids={0: 3, 1: 2, 2: 3, 3: 2})
        round_state.completed_tricks = [
            [
                (0, Card(Suit.HEARTS, Rank.ACE)),
                (1, Card(Suit.HEARTS, Rank.TWO)),
                (2, Card(Suit.HEARTS, Rank.FIVE)),
                (3, Card(Suit.SPADES, Rank.ACE)),
            ]
        ] * 13
        result = round_state.finish()
        self.assertEqual(result.seat_tricks, (0, 0, 0, 13))
        self.assertEqual(result.scores.team0_tricks, 0)
        self.assertEqual(result.scores.team1_tricks, 13)


if __name__ == "__main__":
    unittest.main()
