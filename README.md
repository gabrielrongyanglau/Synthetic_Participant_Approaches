# Synthetic Participant Research Toolkit

A public research prototype for choosing and trying eight synthetic participant approaches (SPAs). Select a research purpose, define the study, identify available information, review a suggestion and generate downloadable datasets with demographic and psychological variables.

## Deploy to Vercel

Upload the contents of this folder to the root of a GitHub repository. Import it into Vercel, select **FastAPI**, and keep the root directory as `./`. Add **OPENAI_API_KEY** as a server-side environment variable, then deploy. No invitations, accounts or database are required. Never upload a completed `.env` file.

When updating the earlier prototype, replace the repository contents with this complete package, including the new `spa/custom.py`, `spa/recommendations.py` and `web/research.js` files. Keep the existing Vercel environment variable. The linked project redeploys after the commit.

AI generation uses **GPT-5.6 Luna**, **medium** reasoning and a 128,000-token output allowance. The research-funded trial currently permits **one approach, one dataset and 100 participants per simulation**. The interface and server both enforce this limit. Larger or repeated runs are unavailable. Using a visitor’s own API key and paying their own costs is planned for a future update, not currently implemented.

Generation time varies with the complexity of the data being generated: simple runs can finish in a few minutes, while runs with many variables or large pilot inputs can take up to an hour. To keep this short, each 100-person dataset is generated as **four parallel requests of 25 participants**. Set `SPA_BATCH_SIZE` to `50` or `100` to change this; `100` reproduces the single-request protocol used in the original MIDUS evaluation. It explains that the research team’s API budget or provider limits may interrupt service. This is not a measured runtime guarantee. Optionally set `SPA_CONTACT_EMAIL` to the team's public support email and `SPA_ESTIMATED_MINUTES` to an updated planning range, such as `60`. Without a configured email, users are directed to contact the person who shared the prototype. Only `OPENAI_API_KEY` is required.

## Repository layout

| Path | Purpose |
| --- | --- |
| `app.py`, `vercel.json`, `requirements.txt` | FastAPI server and Vercel configuration |
| `web/` | The interface: one HTML page, one stylesheet and five scripts |
| `spa/` | Study definitions, prompt assembly, generation, scoring and statistics; `public.py` (readable names) and `numbering.py` (SPA numbering) |
| `config/study.yaml`, `prompts/methods.json` | MIDUS variable definitions and the original method prompts (unchanged) |
| `data/original_study/` | Verified aggregate results shown under Study findings |
| `data/examples/` | Fictional example files (one row per participant) served as upload templates |
| `tests/`, `pytest.ini`, `requirements-dev.txt` | Automated tests (no paid API calls) |
| `analyse.py`, `import_r.py` | Offline reproduction of the original study results |
| `verification/` | Build record, core-file hashes and the original workbook verification summary |
| `web/fonts/` | IBM Plex Sans (SIL Open Font License), subset to Latin |
| `docs/` | User guide, custom studies, data, errors and advice, prompt policy, Vercel operation and verification notes |
| `run.py`, `.env.example` | One-command local preview and the environment-variable template |

## Research console

The interface is a research console: a status bar along the top, side navigation showing each step as to do, locked or completed, the current page in the middle, and an inspector on the right with your selections, the study evidence for the chosen approach, tips and an activity log.

You can try out the toolkit with the MIDUS study used in the proposal, where everything is already set up, or enter your own study. The steps come in this order. The MIDUS demonstration skips step 6, and later steps stay locked until the earlier ones are complete.

1. **Choose your study.** The MIDUS demonstration, which always uses the example inputs supplied with the toolkit, or your own study. Choosing MIDUS shows its 6 demographic characteristics, 38 psychological predictors and 2 outcomes.
2. **Research goal.** The proposal's two goals: generate psychological variables that resemble human responses (Goal 1), or explore relationships among variables, covering patterns and strengths (Goal 2).
3. **Questionnaire.** Demographics first, then psychological measures. For the MIDUS demonstration, tick which of the 6 demographic characteristics and 38 psychological predictors to include (all start ticked, as in the proposal), with both life-satisfaction outcomes always included. For your own study, give a title, then either upload a CSV that lists your variables (a blank template, a completed MIDUS example and column instructions are provided) or enter them on the page: tick common demographics (age group, gender, highest education, marital status, employment status) or add your own, then add measures with definitions, sources, every item and scoring. The questionnaire is confirmed before you continue, and editing it later asks for a new confirmation.
4. **Information.** One choice from six: no participant data, a general population description, population demographic proportions, a small human pilot dataset, actual demographic profiles, or actual demographic and psychological scores. For your own study this is the information you have. The MIDUS demonstration has example information of every kind, so you choose which the simulation uses.
5. **Approach.** One recommended approach with the study result behind it, the other approaches that fit, and a list of all eight approaches showing which fit your information. Study results for every approach are under Study findings.
6. **Inputs** (own study). Only what the chosen approach needs, with templates and instructions for every upload.
7. **Check and generate.** Check inputs, review the summary and confirm before generating. Prompts are read-only. For the MIDUS demonstration, this page also links to the example input and the variable guide.
8. **Datasets.** Progress, previews and duplication flags, then a ZIP with the dataset, codebook and metadata. The codebook maps every exported column to its full name, definition, scoring, allowed values and provenance.

*Overview*, *Study findings*, *Glossary* and *Errors and help* are in the same navigation. Text uses IBM Plex Sans (SIL Open Font License), served from `web/fonts/` so the page makes no third-party requests.

## Study modes

**MIDUS study** preserves the original representative prompts, score definitions and statistical engine. It uses 38 psychological scores, six demographics and life satisfaction at MIDUS 2 and MIDUS 3. The original study benchmark contains 2,709 eligible people. Only invented example records and aggregate study results are distributed.

**My own study** accepts construct definitions, source citations, exact items, response ranges and anchors, reverse coding, predictor/outcome roles and mean, sum or item-only scoring. Define up to 30 constructs and 60 item/demographic fields. Demographic categories are optional and needed only for SPA4, SPA7 and SPA8. They use numeric category codes. Every text field shows an example of how to fill it in. Generated raw items are scored locally, and mean and sum scores require all items. Your own study always uses your own uploaded data for SPA4 to SPA8. Custom studies are a functional extension, not an empirically validated result of the MIDUS study. Sources and measurement validity are not automatically verified. See [Custom studies](docs/CUSTOM_STUDIES.md).

Visitors cannot edit prompts. `prompts/methods.json` is unchanged from the original study. MIDUS runs use the established templates. Custom runs fill those templates with declared data and apply a server-controlled system layer to map historical wave/outcome wording to the custom measures. These custom adaptations do not reproduce the evaluated MIDUS protocol. See [Prompt policy](docs/PROMPT_POLICY.md).

## Approach numbering

The toolkit uses SPA1–SPA8 throughout, numbered as in the revised proposal (Table 3): **SPA7 retains actual demographics only; SPA8 retains actual demographics and psychological scores**. Code, run names (`SPA8_R0001`), upload templates, charts, tables and downloads all use this numbering. The original study's prompt bank and verified result files are kept byte-identical; they number the last two approaches the other way round, and `spa/numbering.py` is the single place that relabels them when they are loaded.

## Upload templates

Uploads apply to your own study. SPA5 to SPA8 uploads have one row per participant and one column per variable. The SPA4 upload has one row per demographic category. Each approach offers a blank template, a completed example with fictional values that passes the checks as it is, and a ZIP with the variable guide and instructions:

| Approach | Upload | Rows |
| --- | --- | --- |
| SPA4 | Target proportions: `variable`, `category`, `category_label` (for reference), `lower` and `upper` (age bands only) and `proportion`. Proportions add up to 1 within each demographic. No participant data. | one per category |
| SPA5, SPA6 | Pilot sample with every variable and both outcomes | exactly 50 |
| SPA7 | Demographic profiles, one per synthetic participant | 100 |
| SPA8 | Demographic and psychological profiles, one per synthetic participant | 100 |

In a custom study, each construct may be supplied as its item columns or as one construct-score column. The supplied fictional examples are the same files offered as templates.

## Variable names

The website and every download use readable variable names such as `optimism_overall`, `age` and `education`. MIDUS source codes are used only inside the preserved scientific engine and never leave the server. `spa/public.py` holds the one mapping between the two; uploads may use the readable names shown in the templates.

## Data handling

No accounts, database, saved run history, browser local storage or application dataset files are used. Inputs and results are processed temporarily and held in the open browser tab. **Download results before refreshing or closing the tab.** The application cannot recover a lost session.

The server uses the owner's key. OpenAI background responses are temporarily retained for polling; the application requests deletion after receipt on a best-effort basis. Provider retention policies still apply. Known-response retrieval can be checked again without another generation. A batch that fails or returns unusable data is requested once more automatically; a submission with an uncertain outcome is not resent, to avoid double charges. Every error message gives a specific cause and advice; see [Errors and advice](docs/ERRORS.md). The public interface permits one 100-person dataset per run.

Public access incurs charges for the owner. Input bounds and same-origin checks do not provide durable account-wide usage limits or protection against determined automated use. Configure hosting/provider usage controls appropriate for the test.

## Local use and tests

With Python 3.12 or 3.13, run `py -3.13 run.py` from the extracted folder and open http://127.0.0.1:8000. Keep PowerShell open. The interface and input checks work without a key; generation needs one. For local AI generation, copy `.env.example` to `.env`, add the key and restart.

```powershell
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 -m pytest -q
```

Tests mock provider requests and make no paid calls (202 tests). See [Verification](docs/VERIFICATION.md), [User guide](docs/USER_GUIDE.md) and [Vercel operation](docs/VERCEL.md). Optional `analyse.py` and `import_r.py` retain the original offline reproduction workflow and historical method IDs. They are not the website's storage mechanism.
