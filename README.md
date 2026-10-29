# Synthetic Participant Research Toolkit

A **synthetic participant approach (SPA)** is a way of asking an artificial intelligence (AI) model to create participant records using specified instructions and information. This toolkit lets anyone choose among eight approaches, prepare inputs and download simulated datasets.

**Public access. No sign-in. No database. No saved run history.** The application keeps inputs and results temporarily in request/browser memory. Users download the results they want to keep before closing or refreshing the tab.

## Deploy on Vercel

1. Extract the ZIP and upload its **contents** to a new GitHub repository. `app.py`, `requirements.txt`, `.python-version`, `vercel.json` and the folders should be at the repository root.
2. In Vercel, import that repository. Select **FastAPI**, keep Root Directory at `./`, and leave Build and Output settings at their defaults.
3. Add just one required **server-side environment variable**:

   ```text
   OPENAI_API_KEY = your actual OpenAI project API key
   ```

4. Click **Deploy**. No database, invitation JSON, username or password is needed. `DATABASE_URL` and `SPA_INVITES_JSON` are not used by this version.
5. Open the deployed site. Try one AI approach with 100 fictional participants and check the download before sharing the URL.

Every AI simulation uses **GPT-5.6 Luna**, **medium reasoning**, and a **128,000-token maximum output allowance per request**. These settings are fixed on the server. Users cannot see the API key or change the model. The owner's OpenAI project must support the model, structured outputs and background Responses. A large token allowance does not guarantee every response will complete.

Anyone reaching the public site can incur API charges on the owner's account. This version has no per-person allowances or database-backed global rate limits. It bounds input sizes, sample sizes and batch sizes and checks browser request origins; these are not protection against determined automated use. Apply hosting/provider usage controls appropriate to your public test. Do not expose paid credentials to untrusted pull-request preview deployments.

## Use the prototype

1. **Choose an approach.** Select your purpose and available information. Read each method's inputs, procedure and generated values.
2. **Prepare and generate.** Choose fictional examples or upload your own CSVs, select **100–1,000 participants**, and preview the instructions. One dataset per selected method is the default; 1–5 repetitions are optional.
3. **Your datasets.** Keep the tab open while requests run. Inspect the preview and quality flags, then download each CSV or one ZIP. If interrupted, valid received batches can be downloaded as clearly marked partial datasets.
4. **Compare with human data**, if needed. Supply a reference with the same variables. The comparison is temporary and does not send that reference to OpenAI.
5. **Study findings** shows the original study's verified aggregate results, separate from the current session.

The **free demonstration** uses fictional numerical rules, not an AI model, and makes no paid calls. It illustrates the workflow and file format. It is not evidence of model performance.

This version uses the study definitions for 38 psychological scores, six demographic variables and life satisfaction at MIDUS 2 and MIDUS 3. It is not an arbitrary-questionnaire generator. The site includes a variable guide, filled upload examples, definitions and metric explanations. See [User guide](docs/USER_GUIDE.md).

## Data handling and recovery

- The application has no database, server-side dataset files, accounts, cookies, analytics, browser local storage or saved session history. It processes request data in memory and sends validated results back to the open browser tab. User-requested downloads save files on the user's own device.
- The browser temporarily holds input snapshots, progress handles, received records, CSVs and comparison results. **Refreshing, closing or clearing the tab loses that session.** The browser's own restore/cache behavior is outside this guarantee; do not rely on it for recovery. Download files before leaving.
- OpenAI generates in background mode so each Vercel request can be short. Requests use `store=false`; OpenAI still temporarily stores background responses for polling, and separate provider retention rules apply. The browser asks the server to delete a response after receiving its validated records. Cleanup is best effort, not a guarantee of zero provider retention. See [Privacy and operation](docs/VERCEL.md).
- Within the same open tab, a temporary retrieval failure can be checked again using the existing response handle. An uncertain submission or invalid response is not automatically regenerated. Without durable state, the application cannot guarantee exactly-once submission or recover a lost submission/response handle.
- Each AI request generates 100 participants. A 1,000-person dataset combines ten requests using the same repetition's input draw. Later batches do not see earlier generated rows. Duplicates and pilot-record matches are retained and flagged across the assembled dataset.
- M4/M7/M8 fixed values are attached from the supplied input snapshots without rounding or imputation. Newly generated values have at most four decimal places.

## Local preview

With Python 3.12 or 3.13 installed, run from the extracted folder:

```powershell
py -3.13 run.py
```

Open **http://127.0.0.1:8000**. Keep PowerShell open; Ctrl+C stops the app. Free demonstrations and prompt previews work without a key. For local AI generation, copy `.env.example` to `.env`, enter the key and restart. Never upload the completed `.env` to GitHub or share it.

## Tests and transparency

```powershell
py -3.13 -m pip install -r requirements-dev.txt
py -3.13 -m pytest -q
```

No database or API key is needed to run the tests. OpenAI calls are mocked. The representative prompt bank, study definitions and statistical formulas are preserved. `analyse.py` and `import_r.py` are optional offline reproducibility tools; they write results only when explicitly run locally and are not the website's storage mechanism. The repository includes invented examples and aggregate study results, not actual human participant microdata.

See [Verification](docs/VERIFICATION.md) for what was tested and its limits. No live Vercel deployment, paid API call or independent security audit was performed. See `LICENSE` for attribution.
