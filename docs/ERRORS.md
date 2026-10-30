# Error and warning catalogue

Generated from `spa/errors.py`. Every error shows a title, what happened and what to do. ‹placeholders› are filled with the specific file, row, column or value.

**Automatic handling.** Requests OpenAI declined (busy, server error) are retried without charge. A batch that fails, returns unusable or repetitive data, expires or stalls is requested again once automatically, and visitors consent to this before generating. A submission with an uncertain outcome waits for the visitor to decide, which avoids a double charge. Progress checks are repeated quietly and pause while the device is offline.

## Uploaded files

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `file_empty` | The file is empty | ‹label› has no rows of data. | Download the template for your approach, fill it in, keep the header row and upload it again. | User action |
| `not_csv` | Upload a CSV file | ‹label› looks like ‹kind›. The toolkit reads comma-separated (CSV) files. | Open the file in Excel or another spreadsheet program and use Save As › CSV UTF-8 (comma delimited). Then upload the .csv file. | User action |
| `wrong_delimiter` | Columns are separated by the wrong character | ‹label› uses "‹delimiter›" between columns. The toolkit needs commas between columns. | Save the file as CSV UTF-8 (comma delimited). Some regional Excel settings save "CSV" files with semicolons, so choose the comma-delimited option. | User action |
| `ragged_rows` | Some rows have the wrong number of values | Row ‹row› of ‹label› has ‹found› values but the header has ‹expected› columns. | Check that row for extra commas, for example decimal commas (3,5 written for 3.5) or a typed note, and for missing cells. Each row needs one value, or a blank, for every column. Use full stops for decimals. | User action |
| `duplicate_columns` | A column name appears twice | ‹label› has more than one column called ‹columns›. | Keep each column once. Download a fresh template if you are unsure which copy to keep. | User action |
| `missing_columns` | Required columns are missing | ‹label› is missing ‹count› required column(s): ‹columns›. | Start from the template for this approach and keep its header row unchanged. Column names must match exactly, including underscores. | User action |
| `identifier_columns` | The file appears to contain personal identifiers | ‹label› has column(s) that look like direct identifiers: ‹columns›. | Delete these columns before uploading. Upload only the variables in the template, with names, emails, phone numbers, addresses and ID numbers removed. | User action |
| `identifier_values` | Personal details found in the data | Row ‹row›, column ‹column› of ‹label› contains what looks like ‹kind›. | Remove all names, emails, phone numbers and ID numbers from the file, then upload it again. | User action |
| `non_numeric_value` | A number column contains text | Row ‹row›, column ‹column› of ‹label› contains "‹value›". This column needs ‹allowed›. | Replace the text with a number from the allowed range, or leave the cell blank if the value is missing and blanks are allowed. Remove labels such as "N/A" or "missing". | User action |
| `decimal_comma` | Use full stops for decimals | Row ‹row›, column ‹column› of ‹label› contains "‹value›", which uses a comma as the decimal mark. | Write decimals with a full stop, for example 3.5. In Excel, change the regional decimal setting or replace commas with full stops before saving as CSV. | User action |
| `value_out_of_range` | A value is outside the allowed range | Row ‹row›, column ‹column› of ‹label› contains ‹value›. Allowed: ‹allowed›. | Correct the value, or leave it blank if it is genuinely missing and blanks are allowed. The variable guide lists every allowed range and code. | User action |
| `not_whole_number` | A whole number is required | Row ‹row›, column ‹column› of ‹label› contains ‹value›, but this column takes whole numbers (‹allowed›). | Round or correct the value. Category columns use the numeric codes in the variable guide. | User action |
| `missing_required_value` | A required value is blank | ‹column› is blank in row(s) ‹rows› of ‹label›. ‹reason› | Fill these cells, or replace the participant with one who has complete data. The row count must stay the same. | User action |
| `wrong_row_count` | The file has the wrong number of participants | ‹label› needs exactly ‹expected› participants, one row each. This file has ‹found› rows. | Add or remove participants so there are exactly ‹expected› rows below the header row. Blank rows at the end of the file also count, so delete them. | User action |
| `too_few_profiles` | Not enough participant profiles | ‹label› needs at least ‹expected› participants, one per synthetic participant. This file has ‹found› rows. | Add profiles until there are at least ‹expected› rows. If you have more, the toolkit selects ‹expected› at random. | User action |
| `duplicate_participants` | The same participant appears many times | ‹label› contains ‹unique› distinct participant(s) across ‹rows› rows. ‹duplicates› row(s) are exact copies of another row. | Check for rows copied or filled down by mistake. Each row must be a different participant, because repeated people distort the averages and relationships the AI learns from. | User action |
| `invalid_input` | Check your inputs | ‹detail› | Correct the file or setting named above, then choose Check inputs again. | User action |

## SPA4 target proportions

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `missing_demographic` | Demographic variables are missing | ‹label› has no proportions for ‹count› demographic variable(s): ‹columns›. | Add rows for each listed variable, with proportions that add up to 1. The template lists every variable and category. | User action |
| `unknown_variable` | Unknown demographic variable | Row ‹row› of ‹label› names "‹value›" in the variable column. | Use one of these variable names: ‹allowed›. Copy them from the template. | User action |
| `unknown_category` | Unknown category code | Row ‹row› of ‹label› gives category "‹value›" for ‹variable›. | Use one of the codes for ‹variable›: ‹allowed›. The category_label column in the template shows what each code means. Use "missing" for the share of participants with no recorded value. | User action |
| `duplicate_category` | A category appears twice | Row ‹row› of ‹label› repeats category "‹value›" for ‹variable›. | Keep one row per category and combine their proportions. | User action |
| `invalid_proportion` | A proportion is outside 0 to 1 | Row ‹row› of ‹label› gives "‹value›" as the proportion for ‹variable›, category ‹category›. | Use a number from 0 to 1, for example 0.25 for 25%. Write decimals with a full stop. Use 0 for a category with no participants. | User action |
| `proportions_sum` | Proportions must add up to 1 | The proportions for ‹variable› add up to ‹total›. | Adjust the ‹variable› rows so their proportions add up to 1, for example 0.48 and 0.52. Percentages that add up to 100 are also accepted. Rounding differences of up to 0.02 are corrected automatically. | User action |
| `invalid_age_band` | An age band needs correcting | Row ‹row› of ‹label›: ‹reason› | Give each age band whole-number ages in the lower and upper columns, from ‹minimum› to ‹maximum›. Each band needs lower at or below upper, and bands must stay separate. | User action |

## Sensitive content

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `sensitive_content` | Sensitive topics detected | Your study materials mention ‹topics› (found in ‹where›). | You can continue if your study has ethics approval, all data are de-identified, and you are allowed to send these materials to OpenAI. Tick the sensitive-topics confirmation, then check inputs again. The AI may still decline some content. If this topic affects you personally, please reach out to someone you trust or a local support service. | User action |
| `prohibited_content` | This content cannot be processed | Your study materials include ‹topics› (found in ‹where›), which the toolkit blocks from generation. | Remove this material. If you believe this is a mistake, contact the research team.  | User action |

## Supporting papers

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `pdf_too_large` | The PDF is too large | ‹name› is ‹size›. The limit is 1.5 MB. | Compress the PDF, upload only the relevant pages, or paste the key findings as text instead. | User action |
| `not_pdf` | Upload a PDF file | ‹name› could not be opened as a PDF. | Upload a .pdf file, or paste the relevant findings as text. | User action |
| `pdf_encrypted` | The PDF is password-protected | ‹name› is locked, so its text cannot be read. | Upload an unlocked copy, or paste the relevant findings as text. | User action |
| `pdf_too_many_pages` | The PDF has too many pages | ‹name› has ‹pages› pages. The limit is 40. | Upload only the relevant section (for example the method and results), or paste the key findings. | User action |
| `pdf_no_text` | No readable text in the PDF | ‹name› contains no selectable text. It is probably a scanned image. | Run text recognition (OCR) on the PDF first, or paste the relevant findings as text. | User action |
| `pdf_too_much_text` | The PDF has too much text | ‹name› contains more than 60,000 characters of text. | Paste only the relevant excerpts, such as key results and measure descriptions. | User action |
| `pdf_unreadable` | The PDF could not be read | Text could not be extracted from ‹name›. The file may be damaged. | Try exporting the PDF again from its source, or paste the relevant findings as text. | User action |

## Starting a run

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `not_configured` | AI generation is offline | The toolkit owner still needs to add the AI service key. | You can still check inputs and preview the instructions. Contact the research team. | User action |
| `consent_missing` | Confirmation needed | Please confirm that these inputs may be sent to OpenAI and that the run uses the research team’s budget. | Tick the data-sharing confirmation under Check and confirm, then try again. | User action |
| `run_limits` | This run is outside the trial limits | Each simulation can use one approach and create one dataset of 100 participants. | Select one approach. This research-funded trial supports one 100-person dataset per run. | User action |
| `inputs_changed` | The inputs changed after they were prepared | The inputs sent for generation differ from the prepared, signed inputs. | Clear this session, check your inputs again and start a new run. Keep files and settings unchanged while a run is starting. | User action |
| `handle_invalid` | This request has expired | The temporary link to an AI request is invalid or more than 24 hours old. | Download anything already received. To generate the missing participants, clear the session and start a new run. | User action |
| `request_too_large` | The inputs are too large to send | The uploaded data and supporting text exceed the 3 MB request limit. | Use a smaller profile file (100 rows is enough), remove unused columns, or include fewer supporting excerpts. | User action |
| `blocked_request` | Request blocked | This request did not come directly from the toolkit page. | Open the toolkit website directly in a new browser tab and try again. | User action |

## AI service: submitting

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `budget_exhausted` | The AI budget has run out | OpenAI declined the request because the research team’s API credit or spending limit has been reached. | Generation is unavailable until the team adds credit. Contact the research team. Download any datasets you have already received. Your inputs stay in this tab until you close it. | User action |
| `service_busy` | The AI service is busy | OpenAI is limiting the number of requests right now. The toolkit retried automatically and the limit is still in place. | Wait a few minutes, then choose Retry failed batches. No charge was made for the declined request. | Server retries immediately (no charge), then the browser retries twice more after a pause |
| `service_unavailable` | The AI service is temporarily unavailable | OpenAI returned a server error. The toolkit retried automatically without success. | Wait a few minutes and choose Retry failed batches. If this continues, check status.openai.com or contact the research team. | Server retries immediately (no charge), then the browser retries twice more after a pause |
| `service_key_invalid` | The AI service key was rejected | OpenAI rejected the toolkit’s service key. | This must be fixed by the toolkit owner. Contact the research team. | User action |
| `service_access_denied` | The account cannot use the AI model | OpenAI refused access to the configured model for the research team’s account. | This must be fixed by the toolkit owner. Contact the research team. | User action |
| `inputs_too_large_for_model` | The inputs are too long for the AI model | The study definitions, pilot records and supporting text together exceed what the model can read in one request. | Shorten supporting excerpts, remove unused constructs, or set fewer participants per request (SPA_BATCH_SIZE). Contact the research team. | User action |
| `request_rejected` | OpenAI rejected the request | OpenAI gave this reason: ‹reason› | Check your study materials for unusual content, then try again. If this repeats, contact the research team with the time of the error. | User action |
| `submission_uncertain` | Submission status unknown | The connection to OpenAI dropped while a batch was being submitted. OpenAI may have accepted and charged it. | Wait a few minutes before retrying, so a duplicate charge is less likely. Then choose Retry failed batches, or contact the research team if you are unsure. | User action |

## AI service: progress and output

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `progress_check_failed` | Progress could not be checked | The toolkit could not reach OpenAI to check progress. Your requests are still running. | The toolkit keeps checking automatically. If this message stays, choose Check progress again. Checking is free and only reads existing requests. | Browser keeps checking progress (free) |
| `response_expired` | A finished batch has expired | OpenAI deleted the result of this batch before the toolkit collected it, usually because the check came late. | The toolkit requests that batch again once automatically. Keep this tab open until all batches are received. | Browser resubmits the batch once automatically (paid) |
| `generation_failed` | A batch failed to generate | OpenAI reported that the batch failed (‹reason›). | The toolkit retries the batch once automatically. If it fails again, choose Retry failed batches later or contact the research team. | Browser resubmits the batch once automatically (paid) |
| `output_too_long` | A batch stopped before it finished | The AI reached its output length limit before generating every participant in the batch. | The toolkit retries once automatically. If this repeats, reduce the number of variables, or ask the owner to set SPA_BATCH_SIZE to 25. | Browser resubmits the batch once automatically (paid) |
| `content_blocked` | The AI service blocked the content | OpenAI’s safety filter stopped this batch. | Review study materials for content that could be flagged (for example graphic descriptions in items or papers). Remove or rephrase it, then start a new run. | User action |
| `model_refused` | The AI declined to generate this data | The model refused the request: "‹reason›" | This usually relates to sensitive study content. Rephrase or remove that content and start a new run. A retry works best after that content is changed. | User action |
| `invalid_output` | The AI returned unusable data | The batch failed checks for participant count, identifiers, fields or value ranges (‹reason›). | The toolkit discards the batch and retries once automatically. If it fails again, choose Retry failed batches. | Browser resubmits the batch once automatically (paid) |
| `repetitive_output` | The AI repeated participants | ‹count› of ‹size› participants in this batch were exact copies of another generated participant. | The toolkit retries the batch once automatically. If repetition continues, the batch is kept and flagged so you can decide whether to use it. | Browser resubmits the batch once automatically (paid) |
| `copied_pilot` | The AI copied pilot participants | ‹count› generated participants in this batch are exact copies of pilot records. | The toolkit retries the batch once automatically. Copies that remain are flagged in the dataset’s quality checks. | Browser resubmits the batch once automatically (paid) |
| `batch_stalled` | A batch took too long | One batch has been generating for more than ‹minutes› minutes, much longer than usual. | The toolkit cancels it and requests that batch again once automatically. If it stalls again, check status.openai.com and try later. | Browser resubmits the batch once automatically (paid) |
| `cancelled` | Batch cancelled | This batch was cancelled before it finished. | Choose Retry failed batches to generate the missing participants (a new paid request). | User action |

## Comparison with human data

| Code | Title | Message | What the user is told to do | Automatic handling |
| --- | --- | --- | --- | --- |
| `reference_unusable` | The human reference cannot be used | ‹detail› | Upload observed human data with the same variable columns as the generated dataset (see the variable guide). Each psychological variable needs at least two different observed values. | User action |
| `no_dataset` | No dataset to compare yet | This tab has no completed dataset yet. | Generate a dataset first, then return to Compare with human data. | User action |

## Warnings (shown with results, download stays available)

| Code | Title | Message | Advice |
| --- | --- | --- | --- |
| `percentages_converted` | Percentages converted to proportions | ‹label› used percentages (totals of 100), so every value was divided by 100. | No action needed. |
| `proportions_rescaled` | Rounded proportions adjusted | The proportions for ‹variables› were scaled slightly so each set adds up to exactly 1. | No action needed if the difference came from rounding. |
| `duplicate_rows` | Some participants are repeated | ‹label› has ‹count› row(s) that exactly repeat another participant. | Check whether rows were copied by mistake. Repeated people give their responses extra weight. |
| `constant_column` | A variable has no variation | ‹column› has the same value (‹value›) for every participant in ‹label›. | Correlations involving this variable will be blank. Check the column was filled correctly. |
| `empty_column` | A variable is completely blank | ‹column› is blank for every participant in ‹label›. | The AI will receive only blanks for this variable. Fill it if you have the values. |
| `ignored_columns` | Some columns were ignored | ‹label› has extra column(s) that the toolkit ignored and left out of the request: ‹columns›. | Only template columns are used. Remove extra columns if they contain anything you did not mean to upload. |
| `missing_codes` | Source missing-value codes were treated as blanks | ‹count› cell(s) in ‹label› used a declared missing-value code (for example 98) and were treated as blank. | No action needed if these codes meant "missing". |
| `missing_tokens` | Text such as "N/A" was treated as blank | ‹count› cell(s) in ‹label› contained a missing-value label such as N/A and were treated as blank. | No action needed if these cells meant "missing". Required values (such as pilot outcomes) still need a number. |
| `repeated_profiles` | Many generated participants are identical | ‹count› of ‹n› participants exactly repeat another generated participant. | Treat this dataset with caution. Consider generating a new dataset, or using an approach with pilot data, and compare with human data before relying on it. |
| `pilot_copies` | Some participants copy the pilot data | ‹count› generated participants are exact copies of pilot records. | Copied pilot records are real people’s responses. Consider removing them before analysis. |
| `no_variation` | A generated variable is constant | ‹column› has the same value for every generated participant. | Correlations with this variable will be blank. Treat results for it with caution. |
| `floor_ceiling` | Scores cluster at the scale limit | ‹share› of generated ‹column› values sit at the scale ‹end› (‹value›). | This may be a ceiling or floor effect, or an artefact of generation. Compare with pilot or human data before interpreting it. |
| `batch_quality` | A batch was kept despite quality issues | ‹detail› | The issue remained after the automatic retry. Review the quality checks before using this dataset. |

## Browser-only errors

Raised in `web/app.js` before anything reaches the server: `offline`, `network_error`, `server_timeout`, `unreadable_response`, `wrong_file_type`, `file_too_large`, `upload_missing`, `review_needed`, `session_exists`, `reference_missing`. Each has a title, message and advice in the same format.
