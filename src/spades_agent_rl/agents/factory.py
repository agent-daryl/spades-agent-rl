from __future__ import annotations

from spades_agent_rl.agents.base import Agent
from spades_agent_rl.agents.heuristic import HeuristicBot
from spades_agent_rl.agents.human import HumanAgent


def make_default_agents(include_human: bool, human_name: str = "You") -> list[Agent]:
    names = ["North", "East", "South", "West"]
    agents: list[Agent] = []
    for seat, default_name in enumerate(names):
        if include_human and seat == 0:
            agents.append(HumanAgent(seat=seat, name=human_name))
        else:
            agents.append(HeuristicBot(seat=seat, name=default_name))
    return agents
