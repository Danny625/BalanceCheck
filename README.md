# BalanceCheck

An advisory agent that helps a game balance designer choose up to three character-review priorities using performance metrics, player feedback, and written game rules.

70-445 Artificial Intelligence for Business Leaders — Product Management Track.
Team: Scott Shu, Elizabeth Hsu, Danny Weng.

## Current status

The working Streamlit app includes configurable review rules, complete roster coverage checks, ranked priorities, evidence, and downloadable run records. Live default-policy and custom-policy practice reviews passed validation. Software checks do not establish held-out model accuracy. See [final product updates and verification](docs/final_updates.md).

## Start here

- [Simplest architecture and exact file responsibilities](docs/architecture.md)
- [Build order and midpoint completion checklist](docs/build_plan.md)
- [Team collaboration](docs/team_workflow.md)
- [Supplied one-page specification](docs/BalanceCheck_Spec.pdf)
- [Synthetic data inventory](data/README.md)
- [Game guide](data/shared/game_guide.md)
- [AI use log](docs/ai_use_log.md)
- [Known weaknesses](docs/known_weaknesses.md)
- [Evaluation and scoring instructions](evaluation/README.md)
- [Sources](docs/sources.md)
- [Verified model choice](docs/model_choice.md)
- [Shared app deployment](docs/deployment.md)
- [Actual practice report](examples/practice/report.md)

## Product experience

Choose a sample scenario, click **Run review**, and receive zero to three ranked priorities with an action, affected skill groups, evidence references, uncertainty, and a next step. Upload mode accepts matching statistics and feedback CSVs for the supplied game. Expand **Review rules** to change thresholds, ranking, or roster scope before running. Each report keeps its original settings; changing inputs shows a previous-review warning until you rerun.

Python calculates the numbers. A hosted language model requests evidence through read-only Python functions and writes the report. A designer approves every investigation and game change.

All supplied game data is synthetic. The agent must not change game data, contact players, prescribe exact buffs/nerfs, invent missing metrics, or follow instructions in player comments.

## What is included now

The original data package is under `data/`, including shared references, a practice scenario, ten logical evaluation cases (twelve scenario folders because two cases are paired), and its supplied generator. The generator has not been executed or modified.

Use `00_practice` for development. Keep evaluation answer keys and the data README out of the agent's evidence. Freeze evaluation criteria before running held-out cases; log all subsequent changes and reruns.

## Run locally

You need Python 3.12 or newer (tested with 3.14), internet access, and a Gemini API key. You do not need a Streamlit account for local use.

1. Download this repository using **Code → Download ZIP**, then unzip it. GitHub Desktop is another option.
2. On a Mac with Python installed, double-click `Launch.command`. The first launch installs dependencies into the project environment. If macOS blocks it, use the terminal steps below.
3. Open the localhost link shown in the terminal, usually `http://localhost:8501`.
4. In the one-time setup panel, enter your Gemini key and click **Check Gemini connection**. Choose an available text model whose free tier you verified in AI Studio, then click **Save setup on this computer**. The setup controls disappear after saving.
5. Select `00_practice` and click **Run AI review**. The key/model are loaded automatically on future launches.
6. Read the priorities, expand the tool/evidence log, and download the report or complete JSON run record. Keep the terminal running; Control+C stops the app.

Install Python from [python.org](https://www.python.org/downloads/) if necessary. Obtain a Gemini key from [Google AI Studio](https://aistudio.google.com/apikey). A ChatGPT/OpenAI key is not a Gemini credential.

### Terminal setup: Mac/Linux

Open a terminal in the downloaded repository folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export BALANCECHECK_LOCAL_SETUP=1
python -m streamlit run app.py
```

### Terminal setup: Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:BALANCECHECK_LOCAL_SETUP="1"
.\.venv\Scripts\python -m streamlit run app.py
```

Windows/cloud setup have not yet been independently verified.

### Save the key once (optional)

The launcher's one-time setup saves the checked key and chosen model into owner-readable `.env.local`, excluded from Git. You can also copy `.env.example` to `.env.local` and configure it manually. Never paste a key in chat. Local setup is enabled only by `BALANCECHECK_LOCAL_SETUP=1`; it is not shown in normal/cloud launches. With model access configured, no key field or model selector is shown to reviewers. To change a saved key/model, edit `.env.local` locally or replace the hosted secret; a hosted change may require restarting the app. Saved local values are read on each rerun.

The configurable default model is `gemini-3.5-flash-lite`, listed with a free API tier when checked November 20, 2026. Quotas and model availability depend on your project. The app does not enable billing, but cannot guarantee zero cost on a project with paid billing already enabled. The owner chooses the model during setup or configures `GEMINI_MODEL`; regular users do not choose models.

## Application files

| File | Job |
| --- | --- |
| `app.py` | Streamlit screen, uploads, Run button, report display/downloads. |
| `data.py` | CSV validation, Pandas calculations, four read-only evidence tools, statistics baseline. |
| `agent.py` | Gemini tool loop, structured report checks, reproducible run records. |
| `instructions.md` | Agent task, boundaries, and evidence-handling rules. |
| `evaluate.py` | Run the same agent for frozen cases and summarize human scoring. |

The model can request rules, performance, character context, and feedback. Python executes only those tools against the selected scenario. No database, separate frontend/backend, agent framework, game-modifying tools, or live player integrations are used.

## Uploads and failures

Upload mode uses the bundled Shardfall Arena roster, references, and guide. Custom games are outside scope. Use UTF-8 CSVs, at most 2 MB/10,000 rows each:

```text
stats.csv: character,update,skill_group,wins,appearances,picks,eligible_selections
feedback.csv: comment_id,author_id,character,update,skill_level,text
```

Use Low/Mid/High groups and patches 3.1/3.2, including current update 3.2. Leave missing counts blank. Missing denominators remain unavailable; impossible counts and unknown roster names produce input errors. Source CSVs are never overwritten. Missing expected characters/groups are shown before review and retained as explicit unavailable records. Reviews with gaps are marked partial.

Reports include up to three priorities, exact Python evidence, uncertainty, and next steps. Failed evidence/schema validation is visibly unaccepted. Failed API calls never silently become baseline reports. Human review remains necessary for semantic correctness.

Original outputs, tool results, model, timestamps, input/code hashes, and validation results are saved under ignored `runs/` and available as downloads. Preserve invalid reports as failure evidence. Share selected synthetic records deliberately.

## Check the software and evaluate the agent

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python evaluate.py --all-evaluation --baseline-only
```

Software tests use test doubles and mock HTTP, not real model outputs. The baseline command makes no API calls and does not measure agent accuracy. Read [evaluation/README.md](evaluation/README.md) before live evaluation: the team must review and freeze keys first, run thirteen executions for ten logical cases, score with two reviewers, and preserve failures verbatim.

## Peer access and deployment

The localhost link only works on the computer running the app. The private repository requires accepted collaborator invitations. Before midpoint handoff, arrange a working reviewer sandbox/credential and verify setup using only these instructions. A repository URL alone does not grant access.

For a browser link without per-user keys, deploy this same repository to Streamlit Community Cloud, select `app.py`, and configure `GEMINI_API_KEY` in private app secrets. The team has deployed the app to Streamlit Community Cloud; this update was verified locally. Never commit keys or put them in screenshots. The final handoff must include working access, not merely ask peers to find their own credentials.

## Troubleshooting

| Symptom | Next step |
| --- | --- |
| Run button disabled | Enter a Gemini key or configure a server key. |
| Access rejected | Check the replacement key and project permissions in AI Studio. |
| Quota reached | Open the project's [active limits](https://aistudio.google.com/rate-limit). Check whether requests/tokens per minute or a daily allowance was exceeded. Follow Google's reported retry delay when present. A new key in the same project does not reset shared quota. |
| Model unavailable | Select an accessible model supporting function calling and structured outputs. |
| Invalid report | Download/preserve the original JSON; inspect validation errors before changing code or prompts. |
| Upload rejected | Check column names, counts, roster, skill groups, and size. |

GitHub stores the project; it does not run the app. The same app runs locally or on Streamlit Community Cloud. A hosted URL is optional because the assignment permits a repository with accessible instructions and credentials/sandbox where needed.

See the [deployment walkthrough](docs/deployment.md) for one-time hosted setup. Visitors do not enter keys or select models; their requests share the configured project quota.
