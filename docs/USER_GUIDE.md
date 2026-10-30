# Using the prototype

A synthetic participant approach (SPA) asks an AI to produce hypothetical participant records from specified information. This tool helps researchers choose and try eight approaches. The generated data require validation before supporting substantive research claims.

## First visit

1. Keep **MIDUS study (recommended)** selected under *Which study?*. MIDUS is the Midlife in the United States study used in the original evaluation.
2. Choose what you want to explore and tick the information you have. The suggested approach is pre-selected; click any other card to choose it instead. One approach is used per simulation. The left-hand panel shows your choice and progress through the four steps.
3. Choose **Continue to inputs**. Keep **Supplied fictional examples** to try an approach without uploading data, or choose your own data and upload the matching CSV.
4. Choose **Check inputs**, review the summary that appears and tick its confirmation.
5. Tick the data-sharing confirmation, choose **Generate 100 participants with AI**, then **Download dataset and codebook (ZIP)** on *Your datasets*. It contains the CSV, variable codebook, metadata and supporting-information record. Generation time varies: simple runs can finish in a few minutes, while complex data can take up to an hour. Participants are generated in several smaller requests that run at the same time.

## Your own study

Select **Use your own study, questionnaire and participant data**. Enter the target population, construct definitions, verified citations, all exact questionnaire items, response scales, scoring and demographic categories. Each item needs a valid response range. Choose predictor/outcome roles. Mean and sum scores require every item. Define at least one demographic. The example study is fictional and is not a validated questionnaire.

Optional context and papers guide a custom adaptation. Add a research question, paste relevant empirical findings, or upload a PDF. Review all extracted text, including table order and symbols, remove unwanted sources and confirm the evidence checkbox. A DOI alone is not a paper upload.

Choose AI generation to use your own participant inputs and reviewed evidence. There is no prompt editor. Our fixed method templates and server-controlled mapping/evidence instructions produce the request. Custom measures and literature-informed simulations have not been validated by the original MIDUS comparison.

## Upload the right information

Every upload has **one row per participant and one column per variable**. Choose *Download the template to revise*, replace the fictional example values with your own data, keep the header row and the number of rows, and upload it. The instructions ZIP adds a blank template, the variable guide and a READ_ME. Remove direct identifiers. Use UTF-8 comma-separated CSV, numeric codes and allowed ranges.

| Public approach | Participant input |
| --- | --- |
| SPA1–SPA3 | No participant CSV. SPA3 uses a population description. |
| SPA4 | A demographic sample of exactly 50 participants. The toolkit matches its proportions when building 100 profiles. |
| SPA5–SPA6 | A pilot sample of exactly 50 participants with demographics, psychological measures and outcomes. All 50 are used. |
| SPA7 | At least 100 demographic profiles. |
| SPA8 | At least 100 demographic and observed psychological predictor profiles. Outcomes are generated. |

MIDUS pilots contain the listed score columns and both life-satisfaction outcomes. Blank predictors are permitted; outcomes must be observed. In a custom study, each construct may be supplied either as all of its item columns or as one construct-score column; when items are supplied, composite scores are calculated by the toolkit. Custom pilot cells must all be complete. Custom SPA8 accepts predictor scores or their items. Fixed missing predictors remain missing. Names, emails and source person IDs are unnecessary.

SPA5 receives pilot records and precomputed summaries. SPA6 receives pilot records and analyzes them within the model. SPA7 generates psychology and outcomes with fixed demographics. SPA8 generates outcomes with fixed demographics and predictors. Profile pools larger than 100 are sampled without replacement; exact-size pools keep their order.

## Start and wait

Review the time/funding notice, authorize sharing with OpenAI for AI runs, then check inputs. Fix any reported issues before continuing. Review the summary and confirm it. Any subsequent settings/input changes require another check. One simulation creates one dataset of 100 people.

Generation time varies: simple runs can finish in a few minutes, while complex data can take up to an hour. The 100 participants are generated as several smaller requests that run at the same time; *Your datasets* shows the status of each batch, the elapsed minutes and the last check time. The page checks existing background requests through short server calls, avoiding an hour-long Vercel function. No percentage is invented while the provider is generating.

Keep the tab open and your device awake. The page handles common problems itself: a busy service is retried after a short wait, a lost connection pauses checking until you are back online, a failed progress check is repeated quietly, and a batch that fails, expires, stalls for more than an hour or returns unusable, repetitive or copied data is requested once more automatically. If a problem remains, each message names the problem and says what to do. If a batch still fails, you can choose **Retry failed batches** (a new paid request for those participants only) or download the participants received so far as a partial CSV. **Cancel generation** stops batches still running. If the research budget is used up, the service key is invalid or a submission is uncertain, the page stops and asks you to contact the research team rather than trying again. Zero failures cannot be guaranteed. Remaining repeated profiles and pilot matches are kept and listed under *Quality notes*.

Uploads are checked before anything is sent: file type, separators, column names, required values, allowed ranges, whole-number codes, row counts, repeated participants and identifying details. Material on sensitive topics such as suicide or self-harm needs an extra confirmation; prohibited content is blocked. The full list of messages and advice is in [Errors and advice](ERRORS.md).

## Download and optional comparison

Download before refreshing or leaving. The prototype has no saved history. The codebook explains every exported column. Metadata records settings, provenance, quality flags and whether evidence was used. The supporting-information JSON records the reviewed text, not the original PDFs.

Optional human comparison uses observed records with the same measures. It is separate from generation and is not sent to OpenAI. Original MIDUS findings under *Study findings* are separate from visitor simulations. One visitor run cannot estimate a Monte Carlo confidence interval.
