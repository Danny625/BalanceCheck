# Team workflow

## Access

The repository is intended to be private. The owner can invite teammates through GitHub Settings → Collaborators. A repository URL alone does not grant access. Teammates need GitHub accounts and must accept their invitations.

## Working together

1. Read the README, architecture, supplied spec, and data inventory.
2. Clone the repository, or use GitHub Desktop if you prefer a visual interface.
3. Pull the latest main branch before starting work.
4. Make a short branch for a task, commit changes, and open a pull request explaining what changed and how it was checked.
5. Have another teammate review changes to guide rules, evaluation keys, or agent behavior before merging.

Do not commit API credentials or private player data. Keep evaluation keys and test-descriptive documents outside the model's evidence. Commit frozen keys before the first evaluation run. Distinguish practice runs, initial evaluation, and later reruns.

## Current repository status

The repository includes the working app, Gemini connection, software tests, and evaluation tools. Live practice runs with default/custom rules are verified; formal evaluation remains separate. Use [CONTRIBUTING.md](../CONTRIBUTING.md) for the current development workflow and [final_updates.md](final_updates.md) for product behavior and verification.
