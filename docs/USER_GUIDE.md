# Using the prototype

A synthetic participant approach (SPA) asks an AI to produce hypothetical participant records from specified information. This tool helps researchers choose and try eight approaches. The generated data require validation before supporting substantive research claims.

## First visit

The side navigation lists the steps in order, each marked to do, locked or completed. A step stays locked until the steps before it are complete. *Your selections* on the right summarises your choices, and *Activity* records what has happened.

1. Under **1 Choose your study**, choose **MIDUS demonstration** to use the example inputs supplied with the toolkit, with nothing to upload. MIDUS is the Midlife in the United States study used in the original evaluation.
2. Under **2 Research goal**, choose your goal. Goal 1 is generating psychological variables that resemble human responses. Goal 2 is exploring relationships among variables, covering their patterns and strengths.
3. Under **3 Your situation**, answer the yes/no questions about what you have so far, for example whether you have collected pilot data.
4. Under **4 Approach**, review the recommendation from Table 6 of the proposal and the study results for all eight approaches, then choose **Continue with SPA…**. Pick another approach from the cards or the table if you prefer. One approach is used per simulation.
5. Under **5 Check and generate**, tick the data-sharing confirmation, choose **Check inputs**, review the summary and tick its confirmation, then choose **Generate 100 participants with AI**.
6. Under **6 Datasets**, choose **Download dataset and codebook (ZIP)**. It contains the CSV, variable codebook, metadata and supporting-information record. Generation time varies: simple runs can finish in a few minutes, while complex data can take up to an hour. Participants are generated in several smaller requests that run at the same time.

Changing the study, goal, situation or approach asks you to confirm the approach again. Messages and advice appear just below the top bar, so they stay in view. To run another simulation, clear the session under *Datasets*. *Start over* in the top bar resets everything.

## Your own study

Under **1 Choose your study**, select **My own study**. Your own study has two extra steps, so it runs from 1 to 8.

After the research goal, **3 Questionnaire** asks for a study title, construct definitions, verified citations, all exact questionnaire items, response scales, scoring and predictor or outcome roles. Each item needs a valid response range. Mean and sum scores require every item. Demographic categories are optional and needed only for SPA4, SPA7 and SPA8. The example study is fictional and is not a validated questionnaire. Choose **Check and continue** to check the definition and move on. Editing the questionnaire later asks for a new check before the later steps open again.

Optional context and papers on the same page guide a custom adaptation. Add a research question, paste relevant empirical findings, or upload a PDF. Review all extracted text, including table order and symbols, remove unwanted sources and confirm the evidence checkbox. A DOI alone is not a paper upload.

After you confirm the approach, **6 Inputs** asks only for what that approach needs, such as a population description for SPA3 or a pilot sample for SPA5. There is no prompt editor. Our fixed method templates and server-controlled mapping/evidence instructions produce the request. Custom measures and literature-informed simulations have not been validated by the original MIDUS comparison.

## Upload the right information

SPA5 to SPA8 uploads have **one row per participant and one column per variable**. The SPA4 upload has one row per demographic category. Each upload offers a *Blank template*, a *Completed example* with fictional values and an instructions ZIP with the variable guide and a READ_ME. The completed example passes the checks as it is, so you can upload it to try the step. Then fill the blank template, or replace the example values with your own, keeping the header row. Remove direct identifiers. Use UTF-8 comma-separated CSV, numeric codes and allowed ranges.

| Public approach | Participant input |
| --- | --- |
| SPA1–SPA3 | No participant CSV. SPA3 uses a population description. |
| SPA4 | Target proportions for each demographic category, adding up to 1 within each demographic. No participant data. The toolkit builds 100 profiles that match them. |
| SPA5–SPA6 | A pilot sample of exactly 50 participants with demographics, psychological measures and outcomes. All 50 are used. |
| SPA7 | At least 100 demographic profiles. |
| SPA8 | At least 100 demographic and observed psychological predictor profiles. Outcomes are generated. |

MIDUS pilots contain the listed score columns and both life-satisfaction outcomes. Blank predictors are permitted; outcomes must be observed. In a custom study, each construct may be supplied either as all of its item columns or as one construct-score column; when items are supplied, composite scores are calculated by the toolkit. Custom pilot cells must all be complete. Custom SPA8 accepts predictor scores or their items. Fixed missing predictors remain missing. Names, emails and source person IDs are unnecessary.

SPA5 receives pilot records and precomputed summaries. SPA6 receives pilot records and analyzes them within the model. SPA7 generates psychology and outcomes with fixed demographics. SPA8 generates outcomes with fixed demographics and predictors. Profile pools larger than 100 are sampled without replacement; exact-size pools keep their order.

## Start and wait

Review the time/funding notice, authorise sharing with OpenAI for AI runs, then check inputs. Fix any reported issues before continuing. Review the summary and confirm it. Any subsequent settings/input changes require another check. One simulation creates one dataset of 100 people.

Generation time varies: simple runs can finish in a few minutes, while complex data can take up to an hour. The 100 participants are generated as several smaller requests that run at the same time. *Datasets* shows the status of each batch, the elapsed minutes and the last check time. The page checks existing background requests through short server calls, avoiding an hour-long Vercel function. No percentage is invented while the provider is generating.

Keep the tab open and your device awake. The page handles common problems itself: a busy service is retried after a short wait, a lost connection pauses checking until you are back online, a failed progress check is repeated quietly, and a batch that fails, expires, stalls for more than an hour or returns unusable, repetitive or copied data is requested once more automatically. If a problem remains, each message names the problem and says what to do. If a batch still fails, you can choose **Retry failed batches** (a new paid request for those participants only) or download the participants received so far as a partial CSV. **Cancel generation** stops batches still running. If the research budget is used up, the service key is invalid or a submission is uncertain, the page stops and asks you to contact the research team rather than trying again. Zero failures cannot be guaranteed. Remaining repeated profiles and pilot matches are kept and listed under *Quality notes*.

Uploads are checked before anything is sent: file type, separators, column names, required values, allowed ranges, whole-number codes, row counts, repeated participants and identifying details. Material on sensitive topics such as suicide or self-harm needs an extra confirmation, and prohibited content is blocked. The full list of messages and advice is in [Errors and advice](ERRORS.md).

## Download

Download before refreshing or leaving. The prototype has no saved history. The codebook explains every exported column. Metadata records settings, provenance, quality flags and whether evidence was used. The supporting-information JSON records the reviewed text, not the original PDFs.

Original MIDUS findings under *Study findings* are separate from visitor simulations. The toolkit does not compare generated datasets with human data, so check a generated dataset against your own human data before relying on it.
