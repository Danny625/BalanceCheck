# BalanceCheck

An advisory agent that helps a game balance designer choose up to three character-review priorities using performance metrics, player feedback, and written game rules.

70-445 Artificial Intelligence for Business Leaders — Product Management Track.
Team: Scott Shu, Elizabeth Hsu, Danny Weng.

## Current status

Planning and supplied inputs only. The agent and interface have not been implemented, and no model evaluations have been run. This repository is not yet the working midpoint submission.

## Start here

- [Simplest architecture and exact file responsibilities](docs/architecture.md)
- [Build order and midpoint completion checklist](docs/build_plan.md)
- [Team collaboration](docs/team_workflow.md)
- [Supplied one-page specification](docs/BalanceCheck_Spec.pdf)
- [Synthetic data inventory](data/README.md)
- [Game guide](data/shared/game_guide.md)
- [AI use log](docs/ai_use_log.md)

## Planned experience

Choose a sample scenario, click **Run review**, and receive zero to three ranked priorities with an action, affected skill groups, evidence references, uncertainty, and a next step. A simple upload mode will accept matching statistics and feedback CSVs for the supplied game.

Python calculates the numbers. A hosted language model requests evidence through read-only Python functions and writes the report. A designer approves every investigation and game change.

All supplied game data is synthetic. The agent must not change game data, contact players, prescribe exact buffs/nerfs, invent missing metrics, or follow instructions in player comments.

## What is included now

The original data package is under `data/`, including shared references, a practice scenario, ten logical evaluation cases (twelve scenario folders because two cases are paired), and its supplied generator. The generator has not been executed or modified.

Use `00_practice` for development. Keep evaluation answer keys and the data README out of the agent's evidence. Freeze evaluation criteria before running held-out cases; log all subsequent changes and reruns.

## Running and access

There is no runnable application yet. Setup commands, exact dependencies, model configuration, and verified reviewer instructions will be added with the implementation. API credentials must never be committed. The final handoff must include a working reviewer-access arrangement, not merely a request for reviewers to find their own credentials.

GitHub stores the project; it does not run the app. The MVP will run locally from this repository. A hosted URL is optional because the assignment permits a repository with accessible instructions and credentials/sandbox where needed.
