# Deployment, privacy and operation

## Required setup

Import the repository into Vercel with **FastAPI**, Root Directory `./`, default Build and Output settings, and `OPENAI_API_KEY` in server-side Environment Variables. Deploy. The application needs no other environment variable. It does not read a database URL or invitation configuration. Remove old variables if copying settings from the earlier repository.

The root `app.py` exports the FastAPI application. `.python-version` selects Python 3.13. `vercel.json` allows a 120-second function duration. OpenAI submission/retrieval calls have a 35-second network timeout and no automatic SDK retries. Model, reasoning and output allowance are fixed to `gpt-5.6-luna`, medium and 128,000.

Keep secrets out of source files, JavaScript and public-prefixed environment variables. Set the key for Production and redeploy after changes. Keep paid credentials out of untrusted preview deployments. A dedicated OpenAI project key makes usage easier to monitor and revoke separately.

## What is and is not stored

The application writes no uploaded participant records, prompts, generated datasets or run histories to a database or server files. It uses no cookies, browser local/session storage, IndexedDB, service workers or analytics. Inputs/results exist temporarily in function request memory and browser memory. Downloads are intentionally saved on the user's device.

A prepared input plan and a signed temporary response handle stay in the open browser tab. The server verifies their signatures before retrieving a response. This prevents visitors from supplying arbitrary OpenAI response IDs to read unrelated responses under the owner's key. It does not create an account or save the session. The domain-separated signing key is derived in server memory from the owner key; no second secret is required. Handles expire after 24 hours and become invalid if the owner rotates the key.

**This is not a promise of zero data retention by infrastructure providers.** OpenAI must process the supplied records to generate responses. Background requests use `store=false`. Current OpenAI documentation describes temporary background-response storage for polling, around 10 minutes; other monitoring retention depends on the project's data controls. After the browser receives validated records, it requests immediate deletion of that response. Deletion is best effort. A closed tab or failed cleanup request may prevent that step. Hosting providers also retain operational metadata under their policies. The application does not deliberately log request/response bodies or credentials; avoid enabling body/debug tracing in production.

## Generation lifecycle

The browser asks the server to prepare method-specific input snapshots. This unpaid preparation performs the same pilot draws, summary calculations and profile validation as before. It then submits one 100-person batch at a time to OpenAI. OpenAI generates in background mode; the browser polls through short server requests. Validated rows return to browser memory. Fixed fields are attached from the exact input snapshot.

All batches within a dataset share that repetition's pilot/profile draw. New repetitions/methods use distinct input-sampling streams. A supplied exact-size pool will recur across repetitions; different draws can overlap. A seed controls input sampling, not model randomness. Multi-batch generation differs from one single request for 1,000 participants.

Duplicate profiles and pilot matches do not stop a run. Invalid counts, IDs, schemas or ranges do stop that batch, without another paid request. Downloads label incomplete datasets as `*_partial.csv`. Completed dataset ZIPs contain a CSV per full dataset and metadata with quality flags and provenance. Full-dataset duplicate checks include matches across batches.

If a progress read fails, choose **Check progress again** in the same tab. This retrieves the existing response rather than submitting another request. The temporary provider response may expire, so check promptly. If submission itself fails before the browser receives its handle, the accepted/billed outcome can be uncertain. The app does not retry automatically. Ask the owner to inspect provider usage before deliberately starting a replacement run. With no durable state, exactly-once delivery, server-crash recovery and cross-tab resumption are not guaranteed.

**Stop after the current batch** receives the current batch and prevents further submissions. **Clear this session** removes the tab's inputs and results; download what is needed first. Closing or refreshing the page loses its active state and does not guarantee that a paid provider request is cancelled.

## Public access and limits

There is no sign-in or account-based quota. The API key remains server-side, but anyone using the public endpoints can incur charges. Application bounds and origin checks do not prevent determined API automation. Vercel firewall/rate controls and OpenAI usage controls can be configured by the owner without adding accounts to this application. Those settings are separate from this repository.

Requests are limited to 3 MB total and upload examples recommend individual files under 2.2 MB. Prepared input plans must fit within 3.5 MB for the web response; select fewer approaches/repetitions if needed. A demonstration requests one approach at a time; the interface handles multi-approach selection sequentially. ZIPs are assembled in browser memory so the whole download is not constrained by a Vercel response-size limit. Optional comparisons may need one dataset at a time if a large group plus its human reference exceeds 3 MB.

## Deployment check

Before sharing, run one 100-person AI simulation with fictional inputs, inspect the preview/CSV/metadata, and check the completed result at the provider. Test the temporary-read recovery flow. No live provider credentials or Vercel account were used while preparing this package.

Official references: [Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi), [OpenAI background mode](https://developers.openai.com/api/docs/guides/background), [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data), [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).
