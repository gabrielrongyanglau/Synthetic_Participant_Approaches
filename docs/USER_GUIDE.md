# Using the prototype

A synthetic participant approach (SPA) asks an AI to produce hypothetical participant records from specified information. This tool helps researchers choose and try eight approaches. The generated data require validation before supporting substantive research claims.

## First visit

The side navigation lists the steps in order, each marked to do, locked or completed. A step stays locked until the steps before it are complete. *Your selections* on the right summarises your choices, and *Activity* records what has happened.

1. Under **1 Choose your study**, choose **MIDUS demonstration** to use the example inputs supplied with the toolkit, with nothing to upload. MIDUS is the Midlife in the United States study used in the original evaluation.
2. Under **2 Research goal**, choose your goal. Goal 1 is generating psychological variables that resemble human responses. Goal 2 is exploring relationships among variables, covering their patterns and strengths.
3. Under **3 Questionnaire**, tick the demographic characteristics, then the psychological predictors, to include. All 6 and all 38 start ticked, as in the proposal. Both life-satisfaction outcomes are always included. Choosing fewer changes what the AI receives, so results can differ from the proposal's. SPA4, SPA7 and SPA8 need at least one demographic characteristic. Choose **Continue**.
4. Under **4 Information**, choose which information the simulation uses. The MIDUS demonstration has example information of every kind, so any option works: no participant data, a general population description, population demographic proportions, a small human pilot dataset, actual demographic profiles, or actual demographic and psychological scores. For your own study, choose what you have.
5. Under **5 Approach**, review the recommendation from Table 3 of the proposal and which of the eight approaches fit your information, then choose **Continue with SPA…**. Pick another approach from the cards or the table if you prefer. One approach is used per simulation.
6. Under **6 Check and generate**, tick the data-sharing confirmation, then choose **Generate 100 participants with AI**. **Check inputs** is optional: it shows a summary of the settings and any problems, without an AI call. The same checks run when you generate.
7. Under **7 Datasets**, choose **Download dataset and codebook (ZIP)**. It contains the CSV, variable codebook and metadata, with only the variables you chose. Generation time varies: simple runs can finish in a few minutes, while complex data can take up to an hour. Participants are generated in several smaller requests that run at the same time.

Changing the study, goal, information or approach asks you to confirm the approach again, and changing the questionnaire asks you to confirm it again. Messages and advice appear just below the top bar, so they stay in view. To run another simulation, clear the session under *Datasets*. *Start over* in the top bar resets everything.

## Your own study

Under **1 Choose your study**, select **My own study**. Your own study has an extra Inputs step, so it runs from 1 to 8.

After the research goal, **3 Questionnaire** asks for a study title and how you want to enter your variables. **Upload a CSV of your variables** offers a blank template and a completed MIDUS example (sex, marital status, optimism and life satisfaction), with a table explaining each column: role, name, code, categories, definition, citation, items, response range, anchors, response type, scoring and reverse-coded items. Items and categories are separated by a vertical bar. A list of the imported variables then appears for you to check. To change anything, edit the CSV and upload it again. The on-page editor appears only with the one-by-one option. **Enter variables one by one** shows the editor directly, starting with the demographic characteristics: tick any of age group, gender, highest education, marital status, employment status, ethnic group and household income, edit their numbered categories, or add your own (up to eight). Then add your psychological measures with construct definitions, verified citations, all exact questionnaire items, response scales, scoring and predictor or outcome roles. Each item needs a valid response range. Mean and sum scores require every item. Demographics are optional and needed only for SPA4, SPA7 and SPA8. Each text field shows an example of how to fill it in. Choose **Continue** to move on. If anything is missing or in the wrong format, a message says what to fix and the next step stays closed. Editing the questionnaire later asks for a new check before the later steps open again.

After you confirm the approach, **6 Inputs** asks only for what that approach needs, such as a population description for SPA3 or a pilot sample for SPA5. There is no prompt editor. Our fixed method templates and server-controlled mapping instructions produce the request. Custom measures have not been validated by the original MIDUS comparison.

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

Review the time/funding notice, authorise sharing with OpenAI for AI runs, then generate. Check inputs first if you want to see the summary. Any reported issues need fixing before generation starts. One simulation creates one dataset of 100 people.

Generation time varies: simple runs can finish in a few minutes, while complex data can take up to an hour. The 100 participants are generated as several smaller requests that run at the same time. *Datasets* shows the status of each batch, the elapsed minutes and the last check time. The page checks existing background requests through short server calls, avoiding an hour-long Vercel function. No percentage is invented while the provider is generating.

Keep the tab open and your device awake. The page handles common problems itself: a busy service is retried after a short wait, a lost connection pauses checking until you are back online, a failed progress check is repeated quietly, and a batch that fails, expires, stalls for more than an hour or returns unusable, repetitive or copied data is requested once more automatically. If a problem remains, each message names the problem and says what to do. If a batch still fails, you can choose **Retry failed batches** (a new paid request for those participants only) or download the participants received so far as a partial CSV. **Cancel generation** stops batches still running. If the research budget is used up, the service key is invalid or a submission is uncertain, the page stops and asks you to contact the research team rather than trying again. Zero failures cannot be guaranteed. Remaining repeated profiles and pilot matches are kept and listed under *Quality notes*.

Uploads are checked before anything is sent: file type, separators, column names, required values, allowed ranges, whole-number codes, row counts, repeated participants and identifying details. Material on sensitive topics such as suicide or self-harm needs an extra confirmation, and prohibited content is blocked. The full list of messages and advice is in [Errors and advice](ERRORS.md).

## Download

Download before refreshing or leaving. The prototype has no saved history. The codebook explains every exported column. Metadata records settings, provenance and quality flags.

Original MIDUS findings under *Study findings* are separate from visitor simulations. The toolkit does not compare generated datasets with human data, so check a generated dataset against your own human data before relying on it.
