# Synthetic Participant Research Toolkit

A public research prototype for choosing and trying eight synthetic participant approaches (SPAs). Select a research purpose, define the study, identify available information, review a suggestion and generate downloadable datasets with demographic and psychological variables.

## Deploy to Vercel

Upload the contents of this folder to the root of a GitHub repository. Import it into Vercel, select **FastAPI**, and keep the root directory as `./`. Add **OPENAI_API_KEY** as a server-side environment variable, then deploy. No invitations, accounts or database are required. Never upload a completed `.env` file.

When updating the earlier prototype, replace the repository contents with this complete package, including the new `spa/custom.py`, `spa/recommendations.py` and `web/research.js` files. Keep the existing Vercel environment variable. The linked project redeploys after the commit.

AI generation uses **GPT-5.6 Luna**, **medium** reasoning and a 128,000-token output allowance. The research-funded trial currently permits **one approach, one dataset and 100 participants per simulation**. The interface and server both enforce this limit. Larger or repeated runs are unavailable. Using a visitor’s own API key and paying their own costs is planned for a future update, not currently implemented.

Before generation, the interface displays a planning estimate of **up to one hour**, depending on variables, complexity and service availability. It explains that the research team’s API budget or provider limits may interrupt service. This is not a measured runtime guarantee. Optionally set `SPA_CONTACT_EMAIL` to the team's public support email and `SPA_ESTIMATED_MINUTES` to an updated planning range, such as `60`. Without a configured email, users are directed to contact the person who shared the prototype. Only `OPENAI_API_KEY` is required.

## Five pages

1. **Choose an approach.** Select a purpose, use the MIDUS setup or define your own questionnaire, and select all available input types. Suggestions explain the empirical evidence and limitations; alternatives remain selectable.
2. **Prepare and generate.** Use fictional examples or upload matching CSVs. Download blank input templates with instructions and filled fictional examples. Check inputs, review the summary and confirm before generating. Prompts are read-only. The free numerical demonstration makes no AI calls.
3. **Your datasets.** Inspect progress, previews and duplication flags. Download a ZIP containing the dataset, a separate codebook and metadata. The codebook maps every exported column to its full name, definition, scoring, allowed values and provenance. Dataset-only and codebook-only CSVs are also available. Repeated profiles are retained and flagged.
4. **Compare with human data.** Optionally upload observed human data using the same measures. Distributions, relationship patterns and relationship strengths are evaluated separately. This reference is not sent to OpenAI.
5. **Study findings.** Explore verified MIDUS charts and practical applications based on the proposal. The original findings are separate from your current simulation.

## Study modes

**MIDUS demonstration** preserves the original representative prompts, score definitions and statistical engine. It uses 38 psychological scores, six demographics and life satisfaction at MIDUS 2 and MIDUS 3. The original study benchmark contains 2,709 eligible people. Only invented example records and aggregate study results are distributed.

**My own study** accepts construct definitions, source citations, exact items, response ranges and anchors, reverse coding, predictor/outcome roles and mean, sum or item-only scoring. Define up to 30 constructs and 60 item/demographic fields. Custom studies must define demographic fields; they use numeric category codes. The filled example includes age group and employment arrangement. Generated raw items are scored locally; mean/sum scores require all items. Custom studies are a functional extension, not an empirically validated result of the MIDUS study. Optional research context, pasted findings and PDFs can inform generation after explicit review. PDFs are extracted in request memory; only reviewed text is sent to the model. Sources and measurement validity are not automatically verified. See [Custom studies](docs/CUSTOM_STUDIES.md).

Visitors cannot edit prompts. `prompts/methods.json` is unchanged from the original study. MIDUS runs use the established templates. Custom runs fill those templates with declared data and apply a server-controlled system layer to map historical wave/outcome wording to the custom measures. Reviewed literature is included only in that system layer as untrusted reference evidence. These custom adaptations do not reproduce the evaluated MIDUS protocol. See [Prompt policy](docs/PROMPT_POLICY.md).

## Method numbering

Public labels follow the revised proposal: **SPA7 retains actual demographics only; SPA8 retains actual demographics and psychological scores**. Original engine IDs, prompt-bank IDs and source aggregate files are unchanged: public SPA7 = original M8; public SPA8 = original M7. Displayed charts, result tables and dataset download names use the public labels. Downloaded metadata records the mapping. See `spa/recommendations.py`.

## Data handling

No accounts, database, saved run history, browser local storage or application dataset files are used. Inputs and results are processed temporarily and held in the open browser tab. **Download results before refreshing or closing the tab.** The application cannot recover a lost session.

The server uses the owner's key. OpenAI background responses are temporarily retained for polling; the application requests deletion after receipt on a best-effort basis. Provider retention policies still apply. Known-response retrieval can be checked again without another generation. Unknown submissions and invalid responses are not automatically regenerated. The public interface permits one 100-person dataset per run.

Public access incurs charges for the owner. Input bounds and same-origin checks do not provide durable account-wide usage limits or protection against determined automated use. Configure hosting/provider usage controls appropriate for the test.

## Local use and tests

With Python 3.12 or 3.13, run `py -3.13 run.py` from the extracted folder and open http://127.0.0.1:8000. Keep PowerShell open. Free demonstrations work without a key. For local AI generation, copy `.env.example` to `.env`, add the key and restart.

```powershell
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 -m pytest -q
```

Tests mock provider requests and make no paid calls. See [Verification](docs/VERIFICATION.md), [User guide](docs/USER_GUIDE.md) and [Vercel operation](docs/VERCEL.md). Optional `analyse.py` and `import_r.py` retain the original offline reproduction workflow and historical method IDs. They are not the website's storage mechanism.
