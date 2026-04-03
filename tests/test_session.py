from __future__ import annotations

import unittest

from spades_agent_rl.agents import make_default_agents
from spades_agent_rl.game import deal_hands
from spades_agent_rl.game.session import SpadesMatch


class SessionTests(unittest.TestCase):
    def test_deal_hands_produces_full_round_distribution(self) -> None:
        hands = deal_hands(seed=7)
        self.assertEqual(set(hands), {0, 1, 2, 3})
        self.assertEqual(sum(len(hand) for hand in hands.values()), 52)
        self.assertTrue(all(len(hand) == 13 for hand in hands.values()))
        self.assertEqual(len({card for hand in hands.values() for card in hand}), 52)

    def test_bots_can_complete_one_round(self) -> None:
        match = SpadesMatch(agents=make_default_agents(include_human=False), target_score=50, seed=11)
        result = match.play_round()
        self.assertEqual(sum(result.seat_tricks), 13)
        self.assertEqual(len(result.seat_tricks), 4)


if __name__ == "__main__":
    unittest.main()
