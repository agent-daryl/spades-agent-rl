# Architecture Notes

## First Principles

- The rules engine must be deterministic and testable without ML code.
- Human evaluation must be a first-class mode, not a side effect of training code.
- Observation and action schemas must be stable before any RL training starts.
- Bots should be swappable: random, heuristic, frozen policy, trainable policy.

## Planned Milestones

1. Deterministic Spades environment and tests
2. Human-vs-bots CLI flow
3. Baseline heuristic agents
4. Stable observation/action encoding
5. Self-play training loop

## Deterministic Engine Scope

- 4 seats with fixed partnership mapping: `0+2` vs `1+3`
- Standard 52-card deck
- Turn order and lead tracking
- Legal card enforcement
- Spades-broken enforcement
- Trick winner resolution
- Round scoring

## Phase 2 Scope

- Runtime prompt asks whether a human wants to play
- Human occupies seat `0` for consistent evaluation
- Three or four heuristic bots can complete a full match
- Match/session flow stays separate from future RL training code
