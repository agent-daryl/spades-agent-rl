from __future__ import annotations

from spades_agent_rl.agents import make_default_agents
from spades_agent_rl.game.session import SpadesMatch, summarize_seat_teams

def main() -> None:
    include_human = _prompt_yes_no("Do you want to play? [y/n]: ")
    human_name = "You"
    if include_human:
        custom_name = input("Enter your name (leave blank for 'You'): ").strip()
        if custom_name:
            human_name = custom_name
    target_score = _prompt_int("Target score [default 200]: ", default=200, minimum=50)

    print("Seat teams:", summarize_seat_teams())
    print("Human occupies seat 0 and partners with seat 2 when enabled.")

    agents = make_default_agents(include_human=include_human, human_name=human_name)
    match = SpadesMatch(agents=agents, target_score=target_score)
    final_scores = match.play_match()
    print()
    print(f"Final score: team 0={final_scores[0]}, team 1={final_scores[1]}")
    print("Match complete.")


def _prompt_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer y or n.")


def _prompt_int(prompt: str, default: int, minimum: int) -> int:
    raw = input(prompt).strip()
    if not raw:
        return default
    if raw.isdigit():
        value = int(raw)
        if value >= minimum:
            return value
    print(f"Using default value {default}.")
    return default


if __name__ == "__main__":
    main()
