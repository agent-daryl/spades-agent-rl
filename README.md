# Spades Agent RL

Fresh rebuild of a Spades self-play project with a clean separation between:

- deterministic game rules
- human evaluation play
- training interfaces
- agent implementations

## Goals

- Support a startup prompt that asks whether a human wants to play.
- Provide a reliable local evaluation path against bots.
- Build toward self-play training without coupling game flow to ad hoc learning logic.
- Keep the codebase simple enough to iterate on from a local AI workstation.

## Initial Structure

- `src/spades_agent_rl/game/`
  - card and rules primitives
- `src/spades_agent_rl/agents/`
  - bot and human agent interfaces
- `src/spades_agent_rl/training/`
  - self-play and RL entry points
- `src/spades_agent_rl/cli/`
  - command-line entry points
- `docs/`
  - architecture and design notes

## Status

Deterministic rules engine scaffold is in progress.

## Play Locally

```bash
PYTHONPATH=src python3 -m spades_agent_rl.cli.main
```

## Local Test Command

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
