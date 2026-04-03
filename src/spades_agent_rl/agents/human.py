from __future__ import annotations

from dataclasses import dataclass

from spades_agent_rl.agents.base import BidContext, PlayContext
from spades_agent_rl.game import Card


@dataclass
class HumanAgent:
    seat: int
    name: str
    is_human: bool = True

    def choose_bid(self, context: BidContext) -> int:
        print()
        print(f"{self.name}, it is your bid.")
        print(f"Current score: team 0={context.team_scores[0]}, team 1={context.team_scores[1]}")
        print(_format_hand(context.hand))
        while True:
            raw = input("Enter your bid (0-13): ").strip()
            if raw.isdigit():
                bid = int(raw)
                if 0 <= bid <= 13:
                    return bid
            print("Invalid bid. Enter an integer from 0 to 13.")

    def choose_card(self, context: PlayContext) -> Card:
        print()
        print(f"{self.name}, it is your turn.")
        if context.current_trick:
            trick_text = ", ".join(f"seat {seat}: {card}" for seat, card in context.current_trick)
            print(f"Current trick: {trick_text}")
        else:
            print("You are leading the trick.")
        print(
            f"Tricks won so far: team 0={context.tricks_won[0] + context.tricks_won[2]}, "
            f"team 1={context.tricks_won[1] + context.tricks_won[3]}"
        )
        print("Your hand:")
        hand = list(context.hand)
        for index, card in enumerate(hand, start=1):
            legal_marker = "*" if card in context.legal_cards else " "
            print(f"  {index:>2}. {card}{legal_marker}")
        print("* legal play")

        while True:
            raw = input("Choose a card by number: ").strip()
            if raw.isdigit():
                chosen_index = int(raw) - 1
                if 0 <= chosen_index < len(hand):
                    chosen_card = hand[chosen_index]
                    if chosen_card in context.legal_cards:
                        return chosen_card
                    print("That card is not a legal play right now.")
                    continue
            print("Invalid choice. Try again.")


def _format_hand(hand: tuple[Card, ...]) -> str:
    grouped: dict[str, list[str]] = {}
    for card in hand:
        grouped.setdefault(card.suit.value, []).append(str(card).split(" of ")[0])
    ordered_suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
    return "\n".join(f"  {suit}: {', '.join(grouped.get(suit, []))}" for suit in ordered_suits)
