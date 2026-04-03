from __future__ import annotations

from dataclasses import dataclass

from spades_agent_rl.agents.base import Agent, BidContext, PlayContext

from .cards import Card
from .spades import RoundResult, SpadesRound, deal_hands, team_for_seat


@dataclass
class MatchState:
    target_score: int = 200
    team_scores: tuple[int, int] = (0, 0)
    dealer: int = 3
    round_number: int = 0


class SpadesMatch:
    def __init__(self, agents: list[Agent], target_score: int = 200, seed: int | None = None) -> None:
        if len(agents) != 4:
            raise ValueError("SpadesMatch requires exactly 4 agents")
        self.agents = sorted(agents, key=lambda agent: agent.seat)
        self.state = MatchState(target_score=target_score)
        self.seed = seed
        self._seed_counter = 0

    def play_match(self) -> tuple[int, int]:
        while max(self.state.team_scores) < self.state.target_score:
            self.play_round()
        return self.state.team_scores

    def play_round(self) -> RoundResult:
        self.state.round_number += 1
        leader = (self.state.dealer + 1) % 4
        hands = deal_hands(seed=self._next_seed())
        bids = self._collect_bids(hands)
        round_state = SpadesRound(hands=hands, bids=bids, leader=leader)

        print()
        print(f"Round {self.state.round_number}")
        print(f"Dealer: seat {self.state.dealer}. Leader: seat {leader}.")
        print(
            "Seats: "
            + ", ".join(f"{agent.name}=seat {agent.seat}/team {team_for_seat(agent.seat)}" for agent in self.agents)
        )
        print(
            f"Bids: team 0 = {bids[0] + bids[2]} ({bids[0]} + {bids[2]}), "
            f"team 1 = {bids[1] + bids[3]} ({bids[1]} + {bids[3]})"
        )

        while not round_state.is_complete:
            if not round_state.current_trick:
                print(
                    f"Starting trick {len(round_state.completed_tricks) + 1}. "
                    f"Leader: {self.agents[round_state.next_seat].name}"
                )
            acting_agent = self.agents[round_state.next_seat]
            card = acting_agent.choose_card(
                PlayContext(
                    seat=acting_agent.seat,
                    hand=tuple(round_state.hands[acting_agent.seat]),
                    legal_cards=tuple(round_state.legal_actions(acting_agent.seat)),
                    current_trick=tuple(round_state.current_trick),
                    completed_tricks=len(round_state.completed_tricks),
                    spades_broken=round_state.spades_broken,
                    bids=dict(bids),
                    tricks_won=round_state.trick_counts_by_seat(),
                )
            )
            winner = round_state.play_card(acting_agent.seat, card)
            print(f"{acting_agent.name} plays {card}")
            if winner is not None:
                trick_text = ", ".join(f"{self.agents[seat].name}: {played_card}" for seat, played_card in round_state.completed_tricks[-1])
                print(f"Completed trick: {trick_text}")
                print(f"Trick won by {self.agents[winner].name}")
                print()

        result = round_state.finish()
        self.state.team_scores = (
            self.state.team_scores[0] + result.scores.team0_score_delta,
            self.state.team_scores[1] + result.scores.team1_score_delta,
        )
        self.state.dealer = (self.state.dealer + 1) % 4

        print(
            "Round result: "
            f"team 0 tricks={result.scores.team0_tricks}, "
            f"team 1 tricks={result.scores.team1_tricks}, "
            f"score delta=({result.scores.team0_score_delta}, {result.scores.team1_score_delta})"
        )
        print(f"Match score: team 0={self.state.team_scores[0]}, team 1={self.state.team_scores[1]}")
        return result

    def _collect_bids(self, hands: dict[int, list[Card]]) -> dict[int, int]:
        bids: dict[int, int] = {}
        seat_order = [(self.state.dealer + offset) % 4 for offset in range(1, 5)]
        for seat in seat_order:
            agent = self.agents[seat]
            bid = agent.choose_bid(
                BidContext(
                    seat=seat,
                    hand=tuple(hands[seat]),
                    team_scores=self.state.team_scores,
                    dealer=self.state.dealer,
                )
            )
            bids[seat] = bid
            print(f"{agent.name} bids {bid}")
        return bids

    def _next_seed(self) -> int | None:
        if self.seed is None:
            return None
        next_seed = self.seed + self._seed_counter
        self._seed_counter += 1
        return next_seed


def summarize_seat_teams() -> str:
    return ", ".join(f"seat {seat}=team {team_for_seat(seat)}" for seat in range(4))
