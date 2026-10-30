"""Error catalogue. Every problem the toolkit can report has a code, a plain-language message,
specific advice and an automatic-handling rule. The browser shows title, message and advice.

`auto` describes what the toolkit does by itself before asking the user:
  'none'      nothing automatic; the user must act
  'retry'     the server retries immediately (requests that were not accepted, so no charge)
  'resubmit'  the browser resubmits that batch once (a new paid request, covered by the consent)
  'repoll'    the browser keeps checking progress (free)
"""
from .service import contact

def _team():return contact()['text']

CATALOGUE={
 # ---------------- Uploaded files
 'file_empty':dict(title='The file is empty',status=400,auto='none',
   message='{label} has no rows of data.',
   advice='Download the template, fill one row per participant, keep the header row and upload it again.'),
 'not_csv':dict(title='This is not a CSV file',status=400,auto='none',
   message='{label} looks like {kind}, not a comma-separated (CSV) file.',
   advice='Open the file in Excel or another spreadsheet program and use Save As › CSV UTF-8 (comma delimited). Then upload the .csv file.'),
 'wrong_delimiter':dict(title='Columns are separated by the wrong character',status=400,auto='none',
   message='{label} uses "{delimiter}" between columns instead of commas, so its columns cannot be read.',
   advice='Save the file as CSV UTF-8 (comma delimited). In some regional Excel settings "CSV" uses semicolons; choose the comma-delimited option.'),
 'ragged_rows':dict(title='Some rows have the wrong number of values',status=400,auto='none',
   message='Row {row} of {label} has {found} values but the header has {expected} columns.',
   advice='Check that row for extra commas, for example decimal commas (3,5 instead of 3.5) or a typed note, and for missing cells. Each row needs one value, or a blank, for every column. Use full stops for decimals.'),
 'duplicate_columns':dict(title='A column name appears twice',status=400,auto='none',
   message='{label} has more than one column called {columns}.',
   advice='Keep each column once. Download a fresh template if you are unsure which copy to keep.'),
 'missing_columns':dict(title='Required columns are missing',status=400,auto='none',
   message='{label} is missing {count} required column(s): {columns}.',
   advice='Start from the template for this approach and keep its header row unchanged. Column names must match exactly, including underscores.'),
 'identifier_columns':dict(title='The file appears to contain personal identifiers',status=400,auto='none',
   message='{label} has column(s) that look like direct identifiers: {columns}.',
   advice='Delete these columns before uploading. The toolkit needs only the variables in the template; names, emails, phone numbers, addresses and ID numbers must never be uploaded.'),
 'identifier_values':dict(title='Personal details found in the data',status=400,auto='none',
   message='Row {row}, column {column} of {label} contains what looks like {kind}.',
   advice='Remove all names, emails, phone numbers and ID numbers from the file, then upload it again.'),
 'non_numeric_value':dict(title='A cell contains text instead of a number',status=400,auto='none',
   message='Row {row}, column {column} of {label} contains "{value}". This column needs {allowed}.',
   advice='Replace the text with a number from the allowed range, or leave the cell blank if the value is missing and blanks are allowed. Remove labels such as "N/A" or "missing".'),
 'decimal_comma':dict(title='Decimal commas are not supported',status=400,auto='none',
   message='Row {row}, column {column} of {label} contains "{value}", which uses a comma as the decimal mark.',
   advice='Use a full stop for decimals (3.5, not 3,5). In Excel, change the regional decimal setting or replace commas with full stops before saving as CSV.'),
 'value_out_of_range':dict(title='A value is outside the allowed range',status=400,auto='none',
   message='Row {row}, column {column} of {label} contains {value}. Allowed: {allowed}.',
   advice='Correct the value, or leave it blank if it is genuinely missing and blanks are allowed. The variable guide lists every allowed range and code.'),
 'not_whole_number':dict(title='A whole number is required',status=400,auto='none',
   message='Row {row}, column {column} of {label} contains {value}, but this column takes whole numbers ({allowed}).',
   advice='Round or correct the value. Category columns use the numeric codes in the variable guide.'),
 'missing_required_value':dict(title='A required value is blank',status=400,auto='none',
   message='{column} is blank in row(s) {rows} of {label}. {reason}',
   advice='Fill these cells, or replace the participant with one who has complete data. The row count must stay the same.'),
 'wrong_row_count':dict(title='The file has the wrong number of participants',status=400,auto='none',
   message='{label} needs exactly {expected} participants (one row each); this file has {found} rows.',
   advice='Add or remove participants so there are exactly {expected} rows, not counting the header row. Blank rows at the end of the file also count; delete them.'),
 'too_few_profiles':dict(title='Not enough participant profiles',status=400,auto='none',
   message='{label} needs at least {expected} participants (one per synthetic participant); this file has {found} rows.',
   advice='Add profiles until there are at least {expected} rows. If you have more, the toolkit selects {expected} at random.'),
 'duplicate_participants':dict(title='The same participant appears many times',status=400,auto='none',
   message='{label} contains only {unique} distinct participant(s) across {rows} rows; {duplicates} row(s) are exact copies of another row.',
   advice='Check that rows were not copied or filled down by mistake. Each row must be a different participant; repeated people distort the averages and relationships the AI learns from.'),
 'invalid_input':dict(title='Check your inputs',status=400,auto='none',
   message='{detail}',advice='Correct the file or setting named above, then choose Check inputs again.'),
 # ---------------- Content
 'sensitive_content':dict(title='Sensitive topics detected',status=409,auto='none',
   message='Your study materials mention {topics} (found in {where}).',
   advice='You can continue if your study has ethics approval, all data are de-identified, and you are allowed to send these materials to OpenAI. Tick the sensitive-topics confirmation, then check inputs again. The AI may still decline some content. If this topic affects you personally, please reach out to someone you trust or a local support service.'),
 'prohibited_content':dict(title='This content cannot be processed',status=400,auto='none',
   message='Your study materials include {topics} (found in {where}), which this toolkit cannot send for generation.',
   advice='Remove this material. If you believe this is a mistake, contact the research team. '),
 # ---------------- Supporting papers
 'pdf_too_large':dict(title='The PDF is too large',status=400,auto='none',
   message='{name} is {size}. The limit is 1.5 MB.',advice='Compress the PDF, upload only the relevant pages, or paste the key findings as text instead.'),
 'not_pdf':dict(title='This file is not a PDF',status=400,auto='none',
   message='{name} could not be opened as a PDF.',advice='Upload a .pdf file, or paste the relevant findings as text.'),
 'pdf_encrypted':dict(title='The PDF is password-protected',status=400,auto='none',
   message='{name} is locked, so its text cannot be read.',advice='Upload an unlocked copy, or paste the relevant findings as text.'),
 'pdf_too_many_pages':dict(title='The PDF has too many pages',status=400,auto='none',
   message='{name} has {pages} pages; the limit is 40.',advice='Upload only the relevant section (for example the method and results), or paste the key findings.'),
 'pdf_no_text':dict(title='No readable text in the PDF',status=400,auto='none',
   message='{name} contains no selectable text. It is probably a scanned image.',advice='Run text recognition (OCR) on the PDF first, or paste the relevant findings as text.'),
 'pdf_too_much_text':dict(title='The PDF has too much text',status=400,auto='none',
   message='{name} contains more than 60,000 characters of text.',advice='Paste only the relevant excerpts, such as key results and measure descriptions.'),
 'pdf_unreadable':dict(title='The PDF could not be read',status=400,auto='none',
   message='Text could not be extracted from {name}. The file may be damaged.',advice='Try exporting the PDF again from its source, or paste the relevant findings as text.'),
 # ---------------- Run setup
 'not_configured':dict(title='AI generation is not connected',status=503,auto='none',
   message='The toolkit owner has not set up the AI service key yet.',
   advice='You can still check inputs and preview the instructions. '+'{team}'),
 'consent_missing':dict(title='Confirmation needed',status=400,auto='none',
   message='Please confirm that these inputs may be sent to OpenAI and that the run uses the research team’s budget.',
   advice='Tick the data-sharing confirmation under Check and confirm, then try again.'),
 'run_limits':dict(title='This run is outside the trial limits',status=422,auto='none',
   message='Each simulation can use one approach and create one dataset of 100 participants.',
   advice='Select one approach. Larger or repeated runs are not available in this research-funded trial.'),
 'inputs_changed':dict(title='The inputs changed after they were prepared',status=400,auto='none',
   message='The inputs sent for generation no longer match the prepared, signed inputs.',
   advice='Clear this session, check your inputs again and start a new run. Do not edit files or settings while a run is starting.'),
 'handle_invalid':dict(title='This request has expired',status=400,auto='none',
   message='The temporary link to an AI request is invalid or more than 24 hours old.',
   advice='Download anything already received. To generate the missing participants, clear the session and start a new run.'),
 'request_too_large':dict(title='The inputs are too large to send',status=413,auto='none',
   message='The uploaded data and supporting text exceed the 3 MB request limit.',
   advice='Use a smaller profile file (100 rows is enough), remove unused columns, or include fewer supporting excerpts.'),
 'blocked_request':dict(title='Request blocked',status=403,auto='none',
   message='This request did not come directly from the toolkit page.',advice='Open the toolkit website directly (not inside another site or an old saved copy) and try again.'),
 # ---------------- AI provider: submission
 'budget_exhausted':dict(title='The AI budget has run out',status=503,auto='none',
   message='OpenAI declined the request because the research team’s API credit or spending limit has been reached.',
   advice='Generation is unavailable until the team adds credit. {team} Download any datasets you have already received; your inputs stay in this tab until you close it.'),
 'service_busy':dict(title='The AI service is busy',status=503,auto='retry',
   message='OpenAI is limiting the number of requests right now. The toolkit retried automatically but the limit is still in place.',
   advice='Wait a few minutes, then choose Retry failed batches. No charge was made for the declined request.'),
 'service_unavailable':dict(title='The AI service is temporarily unavailable',status=503,auto='retry',
   message='OpenAI returned a server error. The toolkit retried automatically without success.',
   advice='Wait a few minutes and choose Retry failed batches. If this continues, check status.openai.com or contact the research team.'),
 'service_key_invalid':dict(title='The AI service key is not working',status=503,auto='none',
   message='OpenAI rejected the toolkit’s service key.',advice='This must be fixed by the toolkit owner. {team}'),
 'service_access_denied':dict(title='The AI model is not available to this account',status=503,auto='none',
   message='OpenAI refused access to the configured model for the research team’s account.',advice='This must be fixed by the toolkit owner. {team}'),
 'inputs_too_large_for_model':dict(title='The inputs are too long for the AI model',status=400,auto='none',
   message='The study definitions, pilot records and supporting text together exceed what the model can read in one request.',
   advice='Shorten supporting excerpts, remove unused constructs, or set fewer participants per request (SPA_BATCH_SIZE). {team}'),
 'request_rejected':dict(title='OpenAI rejected the request',status=400,auto='none',
   message='The request was not accepted: {reason}',advice='Check your study materials for unusual content, then try again. If this repeats, contact the research team with the time of the error.'),
 'submission_uncertain':dict(title='Not sure whether the request was received',status=503,auto='none',
   message='The connection to OpenAI dropped while a batch was being submitted. It may or may not have been accepted and charged.',
   advice='Wait a few minutes before retrying, so a duplicate charge is less likely. Then choose Retry failed batches, or contact the research team if you are unsure.'),
 # ---------------- AI provider: progress and output
 'progress_check_failed':dict(title='Progress could not be checked',status=503,auto='repoll',
   message='The toolkit could not reach OpenAI to check progress. Your requests are still running.',
   advice='The toolkit keeps checking automatically. If this message stays, choose Check progress again. Checking is free and never starts a new request.'),
 'response_expired':dict(title='A finished batch is no longer available',status=503,auto='resubmit',
   message='OpenAI no longer holds the result of this batch, usually because it was checked too late.',
   advice='The toolkit requests that batch again once automatically. Keep this tab open until all batches are received.'),
 'generation_failed':dict(title='A batch failed to generate',status=503,auto='resubmit',
   message='OpenAI reported that the batch failed ({reason}).',
   advice='The toolkit retries the batch once automatically. If it fails again, choose Retry failed batches later or contact the research team.'),
 'output_too_long':dict(title='A batch stopped before it finished',status=503,auto='resubmit',
   message='The AI reached its output length limit before generating every participant in the batch.',
   advice='The toolkit retries once automatically. If this repeats, reduce the number of variables, or ask the owner to set SPA_BATCH_SIZE to 25.'),
 'content_blocked':dict(title='The AI service blocked the content',status=400,auto='none',
   message='OpenAI’s safety filter stopped this batch.',
   advice='Review study materials for content that could be flagged (for example graphic descriptions in items or papers). Remove or rephrase it, then start a new run.'),
 'model_refused':dict(title='The AI declined to generate this data',status=400,auto='none',
   message='The model refused the request: "{reason}"',
   advice='This usually relates to sensitive study content. Rephrase or remove that content and start a new run. Retrying unchanged inputs is unlikely to help.'),
 'invalid_output':dict(title='The AI returned unusable data',status=503,auto='resubmit',
   message='The batch failed checks for participant count, identifiers, fields or value ranges ({reason}).',
   advice='The toolkit discards the batch and retries once automatically. If it fails again, choose Retry failed batches.'),
 'repetitive_output':dict(title='The AI repeated participants',status=200,auto='resubmit',
   message='{count} of {size} participants in this batch were exact copies of another generated participant.',
   advice='The toolkit retries the batch once automatically. If repetition continues, the batch is kept and flagged so you can decide whether to use it.'),
 'copied_pilot':dict(title='The AI copied pilot participants',status=200,auto='resubmit',
   message='{count} generated participants in this batch are exact copies of pilot records.',
   advice='The toolkit retries the batch once automatically. Copies that remain are flagged in the dataset’s quality checks.'),
 'batch_stalled':dict(title='A batch took too long',status=200,auto='resubmit',
   message='One batch has been generating for more than {minutes} minutes, much longer than usual.',
   advice='The toolkit cancels it and requests that batch again once automatically. If it stalls again, check status.openai.com and try later.'),
 'cancelled':dict(title='Batch cancelled',status=200,auto='none',
   message='This batch was cancelled before it finished.',advice='Choose Retry failed batches to generate the missing participants (a new paid request).'),
 # ---------------- Comparison
 'reference_unusable':dict(title='The human reference cannot be used',status=400,auto='none',
   message='{detail}',advice='Upload observed human data with the same variable columns as the generated dataset (see the variable guide). Each psychological variable needs at least two different observed values.'),
 'no_dataset':dict(title='No dataset to compare yet',status=400,auto='none',
   message='There is no completed dataset in this tab.',advice='Generate a dataset first, then return to Compare with human data.'),
}

# Dataset and upload warnings: shown with the result, never block the user.
WARNINGS={
 'duplicate_rows':dict(title='Some participants are repeated',advice='Check whether rows were copied by mistake. Repeated people give their responses extra weight.',
   message='{label} has {count} row(s) that exactly repeat another participant.'),
 'constant_column':dict(title='A variable has no variation',advice='Correlations involving this variable cannot be calculated. Check the column was filled correctly.',
   message='{column} has the same value ({value}) for every participant in {label}.'),
 'empty_column':dict(title='A variable is completely blank',advice='The AI will have no information about this variable from your data. Fill it if you have the values.',
   message='{column} is blank for every participant in {label}.'),
 'ignored_columns':dict(title='Some columns were ignored',advice='Only template columns are used. Remove extra columns if they contain anything you did not mean to upload.',
   message='{label} has column(s) that are not used and were not sent: {columns}.'),
 'missing_codes':dict(title='Source missing-value codes were treated as blanks',advice='No action needed if these codes meant "missing".',
   message='{count} cell(s) in {label} used a declared missing-value code (for example 98) and were treated as blank.'),
 'missing_tokens':dict(title='Text such as "N/A" was treated as blank',advice='No action needed if these cells meant "missing". Required values (such as pilot outcomes) still need a number.',
   message='{count} cell(s) in {label} contained a missing-value label such as N/A and were treated as blank.'),
 'repeated_profiles':dict(title='Many generated participants are identical',advice='Treat this dataset with caution. Consider generating a new dataset, or using an approach with pilot data, and compare with human data before relying on it.',
   message='{count} of {n} participants exactly repeat another generated participant.'),
 'pilot_copies':dict(title='Some participants copy the pilot data',advice='Copied pilot records are real people’s responses, not synthetic ones. Consider removing them before analysis.',
   message='{count} generated participants are exact copies of pilot records.'),
 'no_variation':dict(title='A generated variable does not vary',advice='Correlations with this variable cannot be calculated. Treat results for it with caution.',
   message='{column} has the same value for every generated participant.'),
 'floor_ceiling':dict(title='Scores cluster at the scale limit',advice='This may be a ceiling or floor effect, or an artefact of generation. Compare with pilot or human data before interpreting it.',
   message='{share} of generated {column} values sit at the scale {end} ({value}).'),
 'batch_quality':dict(title='A batch was kept despite quality issues',advice='The automatic retry did not resolve the issue. Review the quality checks before using this dataset.',
   message='{detail}'),
}

class AppError(ValueError,RuntimeError):
    """An error with a catalogue code. Subclasses both ValueError and RuntimeError so older handlers still work."""
    def __init__(self,code,**params):
        if code not in CATALOGUE:raise KeyError(code)
        self.code=code;self.params=params;spec=CATALOGUE[code]
        fill={**params,'team':_team()}
        self.title=spec['title'];self.message=spec['message'].format(**fill);self.advice=spec['advice'].format(**fill).strip()
        self.status=spec['status'];self.auto=spec['auto']
        super().__init__(self.message+' '+self.advice)
    def payload(self):return dict(detail=self.message,code=self.code,title=self.title,advice=self.advice,auto=self.auto)

def warning(code,**params):
    spec=WARNINGS[code];fill={**params,'team':_team()}
    return dict(code=code,title=spec['title'],message=spec['message'].format(**fill),advice=spec['advice'].format(**fill))

AUTO_TEXT={'none':'User action','retry':'Server retries immediately (no charge), then the browser retries twice more after a pause','resubmit':'Browser resubmits the batch once automatically (paid)','repoll':'Browser keeps checking progress (free)'}
GROUPS=[('Uploaded files',['file_empty','not_csv','wrong_delimiter','ragged_rows','duplicate_columns','missing_columns','identifier_columns','identifier_values','non_numeric_value','decimal_comma','value_out_of_range','not_whole_number','missing_required_value','wrong_row_count','too_few_profiles','duplicate_participants','invalid_input']),
 ('Sensitive content',['sensitive_content','prohibited_content']),
 ('Supporting papers',['pdf_too_large','not_pdf','pdf_encrypted','pdf_too_many_pages','pdf_no_text','pdf_too_much_text','pdf_unreadable']),
 ('Starting a run',['not_configured','consent_missing','run_limits','inputs_changed','handle_invalid','request_too_large','blocked_request']),
 ('AI service: submitting',['budget_exhausted','service_busy','service_unavailable','service_key_invalid','service_access_denied','inputs_too_large_for_model','request_rejected','submission_uncertain']),
 ('AI service: progress and output',['progress_check_failed','response_expired','generation_failed','output_too_long','content_blocked','model_refused','invalid_output','repetitive_output','copied_pilot','batch_stalled','cancelled']),
 ('Comparison with human data',['reference_unusable','no_dataset'])]

def catalogue_markdown():
    fill=lambda t:t.replace('{team}','Contact the research team.').replace('{','‹').replace('}','›')
    out=['# Error and warning catalogue','','Generated from `spa/errors.py`. Every error shows a title, what happened and what to do. ‹placeholders› are filled with the specific file, row, column or value.','',
         '**Automatic handling.** Requests OpenAI declined (busy, server error) are retried without charge. A batch that fails, returns unusable or repetitive data, expires or stalls is requested again once automatically; visitors consent to this before generating. A submission whose outcome is uncertain is never resubmitted automatically, to avoid a double charge. Progress checks are repeated quietly and pause while the device is offline.','']
    listed=set()
    for group,codes in GROUPS:
        out+=[f'## {group}','','| Code | Title | Message | What the user is told to do | Automatic handling |','| --- | --- | --- | --- | --- |']
        for c in codes:
            s=CATALOGUE[c];listed.add(c)
            out.append(f"| `{c}` | {s['title']} | {fill(s['message'])} | {fill(s['advice'])} | {AUTO_TEXT[s['auto']]} |")
        out.append('')
    rest=[c for c in CATALOGUE if c not in listed]
    if rest:
        out+=['## Other','','| Code | Title | Message | Advice | Automatic handling |','| --- | --- | --- | --- | --- |']+[f"| `{c}` | {CATALOGUE[c]['title']} | {fill(CATALOGUE[c]['message'])} | {fill(CATALOGUE[c]['advice'])} | {AUTO_TEXT[CATALOGUE[c]['auto']]} |" for c in rest]+['']
    out+=['## Warnings (shown with results; never block)','','| Code | Title | Message | Advice |','| --- | --- | --- | --- |']
    out+=[f"| `{c}` | {s['title']} | {fill(s['message'])} | {fill(s['advice'])} |" for c,s in WARNINGS.items()]
    out+=['','## Browser-only errors','','Raised in `web/app.js` before anything reaches the server: `offline`, `network_error`, `server_timeout`, `unreadable_response`, `wrong_file_type`, `file_too_large`, `upload_missing`, `review_needed`, `session_exists`, `reference_missing`. Each has a title, message and advice in the same format.','']
    return '\n'.join(out)
