'use strict';
// Session state lives only in this tab's memory. Nothing is written to browser storage.
const $=id=>document.getElementById(id);
let cfg,selected=new Set(),session=null,busy=false,reviewedRequest=null;

function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
/* ---------- Errors: every problem shows what happened and what to do ---------- */
class AppError extends Error{constructor(info){super(info.detail||info.message||'Something went wrong.');Object.assign(this,{code:info.code||'error',title:info.title||'Something went wrong',advice:info.advice||'',auto:info.auto||'none'})}}
const CLIENT_ERRORS={
  offline:{title:'You are offline',detail:'This device has lost its internet connection.',advice:'Reconnect to the internet. Running batches continue at OpenAI, and the toolkit resumes checking automatically when you are back online.'},
  network_error:{title:'The connection was interrupted',detail:'The toolkit could not reach its server.',advice:'Check your connection and try again. If generation has started, keep this tab open. Progress checks resume automatically and only read existing requests.'},
  server_timeout:{title:'The server took too long to respond',detail:'The hosting service stopped waiting for a reply ({status}).',advice:'Try again in a moment. Running batches continue, and the toolkit keeps checking them.'},
  unreadable_response:{title:'The server sent an unexpected reply',detail:'The reply could not be read ({status}).',advice:'Try again. If it continues, download any completed datasets and contact the research team.'},
  request_too_large:{title:'The inputs are too large to send',detail:'The uploaded data exceed the 3 MB request limit.',advice:'Use a smaller profile file (100 rows is enough), or remove unused columns.'},
  wrong_file_type:{title:'Upload a CSV file',detail:'{name} has a different file type. The toolkit reads .csv files.',advice:'In Excel or another spreadsheet program, use Save As › CSV UTF-8 (comma delimited), then upload the .csv file.'},
  file_too_large:{title:'The file is too large',detail:'{name} is {size}. The limit is 2.2 MB.',advice:'Upload only the rows and columns in the template. 50 or 100 rows is enough.'},
  upload_missing:{title:'A file is needed',detail:'{label} has no file selected.',advice:'Download the blank template, fill it with your data and choose it here.'},
  session_exists:{title:'A run is already in this tab',detail:'Only one dataset can be generated per session.',advice:'Download its dataset, then choose Clear this session under Datasets before starting another run.'},
  not_configured:{title:'AI generation is offline',detail:'The toolkit owner has not set up the AI service key yet.',advice:'You can still check inputs. Contact the research team to ask when generation will be available.'}
};
function clientError(code,params={}){const t=CLIENT_ERRORS[code],fill=s=>String(s).replace(/\{(\w+)\}/g,(_,k)=>params[k]??'');return new AppError({code,title:t.title,detail:fill(t.detail),advice:fill(t.advice)})}
function errorCard(err,cls='notice error'){
  const box=el('div',undefined,cls);box.setAttribute('role','alert');
  box.append(el('strong',err.title||'Something went wrong','notice-title'),el('p',err.message||String(err),'notice-body'));
  if(err.advice){const a=el('p',undefined,'notice-advice');a.append(el('span','What to do: ','notice-label'),document.createTextNode(err.advice));box.append(a)}
  return box;
}
function notice(text,error=false){const box=$('notice');box.replaceChildren();if(!text)return;const card=error?errorCard(typeof text==='string'?{title:'Something went wrong',message:text}:text):el('div',text,'notice');const close=el('button','Dismiss','notice-close');close.type='button';close.addEventListener('click',()=>box.replaceChildren());card.prepend(close);box.append(card)}
function action(fn){return async(...args)=>{try{notice('');await fn(...args)}catch(e){notice(e instanceof AppError?e:{title:'Something went wrong',message:e.message,advice:'Try again. If it continues, download any completed datasets and contact the research team.'},true);if(e.code==='sensitive_content')showSensitive(e)}}}
function options(node,values){node.replaceChildren();Object.entries(values).forEach(([k,v])=>{const o=el('option',v);o.value=k;node.append(o)})}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const minutes=since=>Math.max(0,Math.floor((Date.now()-since)/60000));

function page(id){
  if(!$(id)||!$(id).classList.contains('page'))id='overview';
  if(typeof Console!=='undefined'&&!Console.available(id))id='study';
  notice('');
  document.querySelectorAll('.page').forEach(e=>e.hidden=e.id!==id);
  document.querySelectorAll('#nav button').forEach(e=>{const on=e.dataset.page===id;e.classList.toggle('active',on);if(on)e.setAttribute('aria-current','page');else e.removeAttribute('aria-current')});
  window.scrollTo(0,0);
  const h=document.querySelector('#'+id+' h1');if(h){h.tabIndex=-1;h.focus({preventScroll:true})}
  if(id==='evidence')action(evidence)();
  if(typeof Console!=='undefined')Console.shown(id);
}

async function api(path,body){
  const options={credentials:'omit',cache:'no-store',headers:{'Content-Type':'application/json','X-SPA-Request':'1'}};
  if(body!==undefined){const data=JSON.stringify(body);if(new TextEncoder().encode(data).length>3000000)throw clientError('request_too_large');options.method='POST';options.body=data}
  if(!navigator.onLine)throw clientError('offline');
  let r;
  try{r=await fetch(path,options)}catch{throw clientError(navigator.onLine?'network_error':'offline')}
  if(!r.ok){
    let x=null;try{x=await r.json()}catch{}
    if(x&&typeof x.detail==='string')throw new AppError(x);
    throw clientError([502,503,504].includes(r.status)?'server_timeout':'unreadable_response',{status:'HTTP '+r.status});
  }
  try{return await r.json()}catch{throw clientError('unreadable_response',{status:'invalid JSON'})}
}
function showSensitive(err){$('sensitiveBox').hidden=false;$('sensitiveTopics').textContent=err.message;$('sensitiveBox').scrollIntoView({block:'center'})}
function warningList(items){
  const list=el('ul',undefined,'warnings');
  for(const w of items){const li=el('li');li.append(el('strong',w.title),el('span',' '+w.message),el('span',' '+w.advice,'warning-advice'));list.append(li)}
  return list;
}

function invalidateReview(){reviewedRequest=null;if($('runReview'))$('runReview').hidden=true;updateRail()}
function csvText(rows){if(!rows.length)return '';const keys=Object.keys(rows[0]),quote=x=>'"'+String(x??'').replaceAll('"','""')+'"';return [keys,...rows.map(r=>keys.map(k=>r[k]))].map(r=>r.map(quote).join(',')).join('\r\n')}
// CSV downloads start with a UTF-8 byte order mark so Excel shows characters such as en dashes correctly.
function saveBlob(blob,name){
  const go=b=>{const u=URL.createObjectURL(b),a=el('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),30000)};
  if(!/\.csv$/i.test(name))return go(blob);
  blob.slice(0,3).arrayBuffer().then(x=>{const u=new Uint8Array(x);go(u[0]===0xEF&&u[1]===0xBB&&u[2]===0xBF?blob:new Blob(['\ufeff',blob],{type:'text/csv;charset=utf-8'}))});
}

const ROWS={5:50,6:50,7:100,8:100};
function inputRule(m){return m===4?'Target proportions: one row per demographic category, giving the share of participants in that category. Proportions add up to 1 within each demographic. 100 demographic profiles are built to match them. No participant data are needed.':m<7?'Pilot sample: exactly 50 participants, one row each, one column per variable, including every outcome. All 50 are used.':m===7?'Participant profiles: exactly 100 participants, one row each, one column per demographic. Each row becomes one synthetic participant.':'Participant profiles: exactly 100 participants, one row each, one column per demographic and psychological score. Each row becomes one synthetic participant, and the AI generates the outcomes.'}
function proportionInstructions(m,custom){return `INPUT TEMPLATE FOR ${Research.methodLabel(m)}

${inputRule(m)}

1. Open template.csv. Each row is one category of one demographic variable.
2. Keep the header row and the variable and category columns as they are. category_label shows what each code means and is for reference only.
3. Replace the example values in the proportion column with your target proportions. Within each variable they add up to 1, for example 0.48 and 0.52. Percentages that add up to 100 are converted automatically, and rounding differences of up to 0.02 are adjusted.
4. ${custom?'Every demographic you defined needs its rows.':'Every demographic needs its rows. For age, lower and upper give each band in whole years. You can change the bands, keeping them within the eligible ages and separate from each other.'}
5. A category you leave out counts as 0. To include participants with no recorded value, add a row with the category missing.
6. Upload the file on the Inputs step. It is checked straight away, and any problems are listed before anything is sent to the AI.
The example proportions are fictional. Replace them with the targets for your population.
`}
function inputInstructions(m,custom){if(m===4)return proportionInstructions(m,custom);return `INPUT TEMPLATE FOR ${Research.methodLabel(m)}

${inputRule(m)}

1. Open template.csv (or the filled example). Each row is one participant, and each column is one variable.
2. Keep the header row exactly as it is. Replace the example values with your own data, keeping exactly ${ROWS[m]} rows.
3. ${m===7?'Fill one column per demographic, using the category codes in the variable guide.':custom?'For each '+(m===8?'psychological predictor':'psychological construct')+', fill either all of its item columns or a single column with its construct score (named with the construct code shown in the variable guide). Composite scores are calculated by the toolkit when items are supplied.':'Each psychological column is a construct score as defined in input_variable_guide.csv.'}
4. Use numeric values and the category codes and ranges in input_variable_guide.csv. ${m<7&&m!==4?'Every cell needs a value except missing psychological predictors in the MIDUS study. Outcomes must be observed.':'Leave a cell blank only where a value is genuinely missing.'}
5. Remove names, emails and other direct identifiers. Save as UTF-8 comma-separated CSV.
6. Upload the file on the Inputs step. It is checked straight away, and any problems are listed before anything is sent to the AI.
The example values are fictional. Replace them with records you are authorised to use.
`}

function table(rows,parent){
  parent.replaceChildren();
  if(!rows.length){parent.append(el('p','No scorable results are available for this view.'));return}
  const wrap=el('div',undefined,'table-wrap'),t=el('table'),head=el('tr'),thead=el('thead'),b=el('tbody');
  Object.keys(rows[0]).forEach(k=>head.append(el('th',k)));thead.append(head);t.append(thead);
  rows.forEach(row=>{const tr=el('tr');Object.values(row).forEach(v=>tr.append(el('td',v===null?'':typeof v==='number'?Number.isInteger(v)?String(v):v.toPrecision(6):String(v))));b.append(tr)});
  t.append(b);wrap.append(t);parent.append(wrap);
}
function tables(bundle,parent){
  parent.replaceChildren();
  [['summary','Approach-level results'],['comparisons','Pairwise approach comparisons'],['variables','Results by psychological variable'],['human','Human reference statistics']].forEach(([key,title])=>{if(!bundle[key])return;const d=el('details');d.append(el('summary',title));const box=el('div');table(bundle[key],box);d.append(box);parent.append(d)});
}

async function reviewInputs(){
  const req=await request(),result=await api('/api/check-inputs',req);reviewedRequest=JSON.stringify(req);
  const labels={approach:'Selected approach',participants:'Participants',input_source:'Input source',mode:'Simulation type',prompt_policy:'Prompt policy',generated_fields:'Values generated per participant',note:'Check result'};
  const rows=Object.entries(result).filter(([k])=>!['api_calls','warnings','sensitive_topics'].includes(k)).map(([k,Value])=>({Setting:labels[k]||k,Value}));
  if(result.sensitive_topics?.length)rows.push({Setting:'Sensitive topics confirmed',Value:result.sensitive_topics.join(', ')});
  const size=cfg.batch_size,count=Math.ceil(100/size);
  rows.splice(2,0,{Setting:'How it is generated',Value:count>1?`${count} AI requests of ${size} participants, run at the same time`:'One AI request of 100 participants'});
  table(rows,$('reviewTable'));
  $('reviewWarnings').replaceChildren();
  if(result.warnings?.length){$('reviewWarnings').append(el('h4',`Please review ${result.warnings.length} note${result.warnings.length>1?'s':''} about your inputs`),warningList(result.warnings))}
  $('runReview').hidden=false;updateRail();
  notice('Inputs checked without an AI call. Review the summary below, then generate when ready.');
  $('runReview').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
}

const uploadMap={4:'proportions_SPA4',5:'pilot_SPA5',6:'pilot_SPA6',7:'profiles_SPA7',8:'profiles_SPA8'};
// MIDUS pilot wording for SPA5 and SPA6 (Prof Kim's text). The supplied 50 rows are fictional, in the format of the proposal's random draw.
const PILOT_SOURCE='In our proposal, 50 participants were randomly selected from the MIDUS dataset to create a pilot sample. This demonstration provides a fictional pilot sample of 50 participants in the same format. ';
const PILOT_TEXT={5:PILOT_SOURCE+'SPA5 uses their demographic information, psychological scores and life-satisfaction outcomes, together with summary statistics calculated from these records, to generate synthetic participants. This pilot sample is already provided, so no upload is required.',
 6:PILOT_SOURCE+'SPA6 gives the AI their demographic information, psychological scores and life-satisfaction outcomes, and asks it to analyse these records itself before generating synthetic participants. This pilot sample is already provided, so no upload is required.'};
const EXAMPLE_TEXT={4:'the example target proportions',5:'the example pilot sample of 50 participants',6:'the example pilot sample of 50 participants',7:'100 example demographic profiles',8:'100 example demographic and psychological profiles'};
function uploadCard(m,old){
  const key=uploadMap[m],d=el('div',undefined,'upload'),label=el('label',`${Research.methodLabel(m)}: upload your ${m===4?'target proportions (one row per category)':(m<7?'pilot sample':'participant profiles')+` (${ROWS[m]} rows)`}`),f=old[key]||el('input');
  f.type='file';f.accept='.csv,text/csv';f.dataset.asset=key;f.onchange=action(async()=>{invalidateReview();inputsChecked=null;showInputCheck();if(f.files[0]){checkFile(f.files[0]);await checkInputsStep(true)}});label.append(f);
  d.append(label,el('p',inputRule(m),'help'));
  const links=el('div',undefined,'link-row');let a;
  const what=m===4?'fictional proportions':`${ROWS[m]} fictional rows`;let empty;
  if(Research.custom()){a=el('button',`Completed example (CSV, ${what})`);a.type='button';a.className='link';a.addEventListener('click',action(()=>Research.downloadTemplate(m)));empty=el('button','Blank template (CSV)');empty.type='button';empty.className='link';empty.addEventListener('click',action(()=>Research.emptyTemplate(m)))}
  else{a=el('a',`Completed example (CSV, ${what})`);a.href=`/api/example/SPA${m}_template.csv`;a.download=`SPA${m}_completed_example.csv`;empty=el('a','Blank template (CSV)');empty.href='/api/template/'+m;empty.download=`SPA${m}_blank_template.csv`}
  const blank=el('button','Instructions and variable guide (ZIP)');blank.type='button';blank.className='link';
  blank.onclick=action(async()=>{if(Research.custom())await Research.blankTemplate(m);else{const [t,e]=await Promise.all([fetch('/api/template/'+m,{cache:'no-store'}),fetch(`/api/example/SPA${m}_template.csv`,{cache:'no-store'})]);if(!t.ok||!e.ok)throw Error('The template could not be downloaded. Try again.');saveBlob(makeZip({'template.csv':await e.text(),'blank_template.csv':await t.text(),'input_variable_guide.csv':csvText(cfg.variable_guide),'READ_ME.txt':inputInstructions(m,false)}),`SPA${m}_template_and_instructions.zip`)}});
  links.append(empty,a,blank);d.append(links,el('p','The completed example shows a filled template with fictional values. It passes the checks as it is, so you can upload it to try this step, then replace the values with your own data.','help'));return d;
}
// Inputs step: the upload is checked as soon as it is chosen and again on Continue, so problems show on the step where the file is uploaded.
let inputsChecked=null;
function showInputCheck(text,warnings,error){const box=$('inputCheck');box.replaceChildren();box.hidden=!text&&!error;box.className='input-check'+(error?' bad':warnings?.length?' warn':' ok');
  if(error){box.append(errorCard(error,'notice error'));return}
  if(text)box.append(el('p',text));if(warnings?.length){box.append(el('h4',`Please review ${warnings.length} note${warnings.length>1?'s':''} about your file`),warningList(warnings))}}
async function checkInputsStep(quiet=false){
  const req=await request(),key=JSON.stringify(req);if(inputsChecked===key)return;
  try{const r=await api('/api/check-upload',req);inputsChecked=key;
    const rows=Object.values(r.rows||{})[0];showInputCheck(rows!==undefined?`File checked: ${rows} rows, ready for the next step.`:'Inputs checked, ready for the next step.',r.warnings)}
  catch(e){inputsChecked=null;showInputCheck('',null,e);if(!quiet)throw e}
}
const CSV_HELP=m=>'Fill the blank template, or replace the values in the completed example with your own. '+(m===5||m===6||m===8?'Each '+(m===8?'predictor':'measure')+' can be supplied either as its individual item columns or as one score column. ':'')+'Keep the header row unchanged, use the numeric codes in the variable guide, remove names and other direct identifiers, and save as UTF-8 CSV. The file is checked as soon as you choose it, and any problems are listed here before anything is sent to the AI.';
const GUIDE_INTRO={4:'The demographic codes and categories your proportions file uses.',5:'The columns and allowed values for your pilot sample. Every item, demographic and outcome needs a value.',6:'The columns and allowed values for your pilot sample. Every item, demographic and outcome needs a value.',7:'The demographic columns and allowed values for your participant profiles. Blank cells mean missing values.',8:'The demographic and predictor columns and allowed values for your participant profiles. Blank cells mean missing values. Outcomes are generated, so leave them out.'};
function chosenFiles(){return [...$('uploads').querySelectorAll('input')].filter(x=>x.files&&x.files[0])}
function usesExamples(){
  const m=[...selected][0];if(!uploadMap[m])return !Research.custom();
  if(!Research.custom())return !chosenFiles().length;
  return false;
}
function inputs(){
  invalidateReview();
  $('n').value='100';$('repetitions').value='1';
  const m=[...selected][0],custom=Research.custom(),needs=!!uploadMap[m];
  $('populationLabel').hidden=!selected.has(3);
  $('csvHelp').hidden=!custom||!needs;$('guideHelp').hidden=!needs;
  if(custom&&needs){$('csvHelpText').textContent=CSV_HELP(m);$('guideIntro').textContent=GUIDE_INTRO[m]||GUIDE_INTRO[5];Research.showGuide()}
  $('variableGuideLink').hidden=custom;
  const own={};$('uploads').querySelectorAll('input').forEach(x=>own[x.dataset.asset]=x);
  $('uploads').replaceChildren();
  $('dataHeading').textContent=m?`Data for ${Research.methodLabel(m)}`:'Data for this approach';
  const name=m?`SPA${m}`:'This approach';let summary,blocked=false;
  if(!needs)summary=`${name} needs no participant data. The AI works from the study definitions${m===3?' and the population description below':''}. Choose Next: check and generate to continue.`;
  else if(!custom&&[4,7,8].includes(m)&&!Research.demographicCount()){summary=`${name} keeps demographic details fixed, so it needs at least one demographic characteristic. Tick some under Questionnaire.`;blocked=true}
  else if(!custom){summary=PILOT_TEXT[m]||`${name} uses ${EXAMPLE_TEXT[m]} supplied with the MIDUS demonstration. Nothing needs uploading.`;$('exampleFile').href=`/api/example/SPA${m}_template.csv`;$('exampleFile').download=`SPA${m}_example_input.csv`}
  else if([4,7,8].includes(m)&&!Research.demographicCount()){summary=`${name} keeps demographic details fixed, so it needs demographic categories. Add them under Questionnaire, choose Continue, then return here.`;blocked=true}
  else{summary=`Upload ${m===4?'your target proportions':m<7?'your pilot sample of exactly 50 participants':'your participant profiles'} below.`;$('uploads').append(uploadCard(m,own))}
  $('dataSummary').textContent=summary;$('confirmInputs').disabled=blocked;inputsChecked=null;showInputCheck();
  $('exampleLink').hidden=custom||!needs;
  $('total').textContent='';
  updateRail();
}

function updateRail(){if(typeof Console!=='undefined')Console.refresh()}

async function request(){
  if(Research.custom())await Research.refreshTools();
  if(!selected.size)throw new AppError({title:'Choose an approach',detail:'No approach is selected.',advice:'Go back to Approach and choose one approach.'});
  const assets={};
  const examples=usesExamples();
  for(const input of $('uploads').querySelectorAll('input')){
    const f=input.files[0],label=input.parentElement.firstChild.textContent.trim();
    if(!f){if(examples)continue;throw clientError('upload_missing',{label})}
    checkFile(f);
    assets[input.dataset.asset]=await f.text();
  }
  return {sensitive_ack:$('sensitiveAck').checked,goal:Research.goal(),study:Research.study(),midus_fields:Research.midusFields(),methods:[...selected].sort(),n:Number($('n').value),repetitions:Number($('repetitions').value),seed:Number($('seed').value),examples,population:$('population').value,assets,consent:$('consent').checked};
}

function metadata(){
  const size=session.settings.batch_size;
  return {schema_version:'4.5',study_brief:session.brief,approach_numbering:'SPA1–SPA8 as in the revised proposal: SPA7 uses demographic-only profiles, and SPA8 uses demographic and psychological profiles.',source:session.source,settings:session.settings,model:cfg.model,reasoning_effort:cfg.reasoning,
    validation_status:'Not evaluated against a human reference',datasets:Object.keys(session.details).length,records:Object.values(session.details).reduce((n,d)=>n+d.count,0),
    input_provenance:Object.fromEntries(Object.entries(session.contexts).map(([run,ctx])=>[run,ctx.provenance])),
    quality_flags:Object.fromEntries(Object.entries(session.details).map(([run,d])=>[run,d.quality])),
    batching:`${size} participants per AI request, ${Math.ceil(session.settings.n/size)} requests per dataset ran in parallel. Each request sees only its own participants.${size<100?' The original MIDUS evaluation generated 100 participants per request.':''}`,
    storage:'Held in browser memory for download. No accounts, database or application-saved run history. OpenAI processing/retention policies still apply.',
    sampling_note:'Separate method/repetition random streams are used for input draws. Exact-size pools recur across repetitions, and supplied pools may overlap. AI responses vary between runs with the same seed.'};
}
function downloadAll(){
  const files={};
  for(const [run,d] of Object.entries(session.details)){files[Research.runLabel(run)+'.csv']=d.csv;files['codebook.csv']=d.codebook_csv}
  files['metadata.json']=JSON.stringify(metadata(),null,2);
  saveBlob(makeZip(files),'synthetic_participant_datasets.zip');
}
function checkFile(f){
  if(!/\.(csv|txt)$/i.test(f.name))throw clientError('wrong_file_type',{name:f.name});
  if(f.size>2200000)throw clientError('file_too_large',{name:f.name,size:(f.size/1e6).toFixed(1)+' MB'});
}
async function finalise(run){const records=session.records[run];const result=await api('/api/dataset',{name:run,records,study:session.settings.study,midus_fields:session.settings.midus_fields,pilot:session.contexts[run]?.pilot??null});session.details[run]={...result,count:records.length}}

/* ---------- Parallel batched generation with automatic recovery ----------
   Free:  requests OpenAI declined (busy/server error) are retried after a pause; progress checks are repeated.
   Paid:  a batch that fails, returns unusable or repetitive data, expires or stalls is resubmitted ONCE automatically.
   Never: a submission whose outcome is uncertain is not resubmitted automatically (possible double charge). */
const BATCH_STATE={new:'Waiting to submit',submitted:'Submitted',queued:'Queued',in_progress:'Generating',done:'Received',failed:'Failed',cancelled:'Cancelled',waiting:'Waiting to retry'};
const PAID_RETRIES=1,FREE_RETRIES=2,FREE_WAIT=30000,STALL_MINUTES=60,POLL_FAILURES=6;
const pendingChunk=c=>['submitted','queued','in_progress'].includes(c.status);
const NO_RETRY=['inputs_changed','handle_invalid','inputs_too_large_for_model'];
const STOP_ALL=['budget_exhausted','service_key_invalid','service_access_denied','inputs_changed','handle_invalid','not_configured','inputs_too_large_for_model'];
function makeChunks(n,size){const out=[];for(let offset=0;offset<n;offset+=size)out.push({offset,end:Math.min(n,offset+size),status:'new',records:null,handle:null,error:null,paid:0,free:0,pollFails:0,notes:[]});return out}
async function release(s,c,cancel=false){if(!c.handle)return;try{const r=await api('/api/release',{handle:c.handle,cancel});if(!r.released)s.cleanupFailed=true}catch{s.cleanupFailed=true}c.handle=null}
function fail(c,err){c.status='failed';c.error={code:err.code,title:err.title,message:err.message||err.detail,advice:err.advice}}
function autoResubmit(s,c,err){
  if(c.paid>=PAID_RETRIES)return false;
  c.paid++;c.status='new';c.records=null;c.notes.push(`${err.title}. Requested again automatically.`);s.autoRetries=(s.autoRetries||0)+1;return true;
}
async function submitChunk(s,run,c){
  c.status='submitted';c.error=null;c.started=Date.now();c.pollFails=0;
  try{const r=await api('/api/submit',{ticket:s.ticket,run,offset:c.offset,context:s.contexts[run]});c.handle=r.handle;c.status=r.status==='queued'||r.status==='in_progress'?r.status:'submitted'}
  catch(e){
    if(e.auto==='retry'&&c.free<FREE_RETRIES){c.free++;c.status='waiting';c.retryAt=Date.now()+FREE_WAIT*c.free;c.notes.push(`${e.title}. Trying again automatically (no charge).`);return}
    fail(c,e);if(STOP_ALL.includes(e.code))s.halt=e;
  }
}
async function pollChunk(s,run,c){
  if(minutes(c.started)>=STALL_MINUTES){
    await release(s,c,true);
    const err={code:'batch_stalled',title:'A batch took too long',message:`This batch ran for more than ${STALL_MINUTES} minutes.`,advice:'Cancelled and requested again automatically. If it stalls again, try later.'};
    if(!autoResubmit(s,c,err))fail(c,{...err,advice:'Choose Retry failed batches later, or check status.openai.com.'});return;
  }
  let result;
  try{result=await api('/api/poll',{handle:c.handle,context:s.contexts[run]});c.pollFails=0}
  catch(e){
    if(['inputs_changed','handle_invalid'].includes(e.code)){fail(c,e);return}
    c.pollFails++;if(c.pollFails>=POLL_FAILURES)throw e;return;  // keep checking quietly; surface only if it persists
  }
  if(result.status==='queued'||result.status==='in_progress'){c.status=result.status;return}
  await release(s,c);
  if(result.status==='completed'){
    if(result.issue&&autoResubmit(s,c,result.issue))return;
    if(result.issue)c.quality={code:'batch_quality',title:'A batch was kept despite quality issues',message:`Participants ${c.offset+1}–${c.end}: ${result.issue.detail}`,advice:'The automatic retry did not resolve this. Review the quality checks before using this dataset.'};
    c.records=result.records;c.status='done';return;
  }
  const err=new AppError(result);
  if(result.auto==='resubmit'&&autoResubmit(s,c,err))return;
  fail(c,err);if(STOP_ALL.includes(result.code))s.halt=err;
}
async function drive(){
  if(busy||!session)return;
  busy=true;const s=session;s.active=true;s.pollError=null;render();
  try{
    for(const run of s.order){
      if(s.details[run])continue;
      const chunks=s.chunks[run];
      while(session===s&&!s.stop){
        if(s.halt){for(const c of chunks)if(c.status==='new'||c.status==='waiting')fail(c,{...s.halt,message:'Not submitted: '+s.halt.message});break}
        const due=chunks.filter(c=>c.status==='new'||(c.status==='waiting'&&Date.now()>=c.retryAt));
        if(due.length){s.message=`Submitting ${due.length} request${due.length>1?'s':''}…`;render();await Promise.all(due.map(c=>submitChunk(s,run,c)));render();continue}
        if(!navigator.onLine){s.message='You are offline. Checking resumes automatically when the connection returns. Running batches continue at OpenAI.';render();await sleep(3000);continue}
        const waiting=chunks.filter(pendingChunk);
        if(!waiting.length&&!chunks.some(c=>c.status==='waiting'))break;
        try{await Promise.all(waiting.map(c=>pollChunk(s,run,c)))}
        catch(e){s.pollError=e;s.message='Progress checks keep failing. Your batches are still running at OpenAI.';notice(e,true);break}
        const done=chunks.filter(c=>c.status==='done').length;
        s.message=`${done} of ${chunks.length} batches received. Elapsed: ${minutes(s.started)} min. Last checked ${new Date().toLocaleTimeString('en-GB')}. Checking reads existing requests and is free.`;
        render();
        if(chunks.some(c=>pendingChunk(c)||c.status==='waiting'))await sleep(5000);
      }
      if(chunks.every(c=>c.status==='done')){
        s.records[run]=chunks.flatMap(c=>c.records).sort((a,b)=>a.participant_id-b.participant_id);
        try{await finalise(run);s.message=`Complete in ${Math.max(1,minutes(s.started))} min.${s.autoRetries?` ${s.autoRetries} batch${s.autoRetries>1?'es were':' was'} retried automatically.`:''} Download your dataset before leaving this tab.`}
        catch(e){s.message='All participants were received and are held in this tab, but preparing the download failed: '+e.message+' Use the partial CSV download, or try Check progress again.';notice(e,true)}
      }else if(chunks.some(c=>c.status==='failed'||c.status==='cancelled')&&!chunks.some(c=>pendingChunk(c)||c.status==='waiting')){
        s.failed=true;s.message=s.halt?`${s.halt.title}. ${s.halt.advice}`:'Some batches did not complete. Their reasons and advice are listed below. You can retry them (a new paid request) or download the participants received so far.';
        if(s.halt)notice(s.halt,true);
      }
    }
  }finally{
    s.active=false;busy=false;
    if(s.discardAfter){clearSession();notice('Session cleared.')}
    render();
  }
}
window.addEventListener('online',()=>{if(session&&!session.active&&session.order.some(r=>session.chunks[r].some(pendingChunk)))action(drive)()});
async function cancelRun(){
  if(!session||!window.confirm('Cancel the batches still generating? Batches already received are kept. Requests already started may still incur charges.'))return;
  const s=session;s.stop=true;
  for(const run of s.order)for(const c of s.chunks[run])if(pendingChunk(c)||c.status==='waiting'||c.status==='new'){await release(s,c,true);c.status='cancelled';c.error={title:'Cancelled',message:'Cancelled by you.',advice:'Choose Retry failed batches to generate these participants (a new paid request).'}}
  s.message='Generation cancelled. Participants already received are kept.';render();
}
async function retryFailed(){
  const s=session;if(!s||s.active)return;
  for(const run of s.order)for(const c of s.chunks[run])if(c.status==='failed'||c.status==='cancelled'){c.status='new';c.error=null;c.records=null;c.free=0}
  s.failed=false;s.stop=false;s.halt=null;await drive();
}
// Clearing removes the run's results and progress. The uploaded file is kept, so the same inputs can be generated again.
function clearSession(){session=null}
async function discard(){
  if(!session)return;
  if(!window.confirm('Clear this session? Download your datasets first. Results and progress will be removed from this tab.'))return;
  if(session.active){session.stop=true;session.discardAfter=true;notice('The session will clear once the current check returns. Requests already started may still incur charges.');return}
  clearSession();render();notice('Session cleared. No saved history is available.');
}

async function start(){
  if(session){page('datasets');throw clientError('session_exists')}
  if(!cfg.configured)throw clientError('not_configured');
  if(busy)return;
  busy=true;$('generate').disabled=true;
  try{
    const req=await request();
    if(!req.consent)throw new AppError({code:'consent_missing',title:'Confirmation needed',detail:'Please confirm that these inputs may be sent to OpenAI and that the run uses the research team’s budget.',advice:'Tick the data-sharing confirmation under Check and confirm, then try again.'});
    const brief=Research.snapshot();
    notice('Preparing the inputs in memory…');
    const plan=await api('/api/prepare',req);plan.settings.study=req.study;plan.settings.midus_fields=req.midus_fields;
    const order=Object.keys(plan.contexts);
    session={...plan,brief,order,records:{},details:{},chunks:Object.fromEntries(order.map(run=>[run,makeChunks(plan.settings.n,plan.settings.batch_size)])),active:false,started:Date.now(),autoRetries:0};
    busy=false;notice('');page('datasets');await drive();
  }finally{busy=false;$('generate').disabled=false;render()}
}

/* ---------- Datasets page ---------- */
function batchList(s,run){
  const list=el('ol',undefined,'batches');
  for(const c of s.chunks[run]){
    const li=el('li',undefined,'batch batch-'+c.status);
    li.append(el('span',`Participants ${c.offset+1}–${c.end}`,'batch-range'),el('span',BATCH_STATE[c.status],'batch-state'));
    for(const n of c.notes)li.append(el('span',n,'batch-note'));
    if(c.error){const e=el('span',undefined,'batch-error');if(s.halt&&c.error.code===s.halt.code)e.append(el('strong',c.error.title+'. '),document.createTextNode('See the message above.'));else e.append(el('strong',c.error.title+'. '),document.createTextNode(c.error.message+' '),el('em','What to do: '+c.error.advice));li.append(e)}
    list.append(li);
  }
  return list;
}
function render(){
  const s=session,complete=s?Object.keys(s.details).length:0;
  const anyFailed=!!s&&s.order.some(run=>s.chunks[run].some(c=>c.status==='failed'||c.status==='cancelled'));
  const anyPending=!!s&&s.order.some(run=>s.chunks[run].some(pendingChunk));
  $('emptyResults').hidden=!!s;$('clearResults').hidden=!s;$('downloadAll').hidden=!complete;
  $('stopRun').hidden=!s||!anyPending;
  $('retryRun').hidden=!s||s.active||!anyFailed||!!(s.halt&&NO_RETRY.includes(s.halt.code));
  $('checkAgain').hidden=!s||s.active||!anyPending;
  $('generate').disabled=!!s?.active||!cfg?.configured;
  $('jobDetail').replaceChildren();$('datasetList').replaceChildren();
  updateRail();
  if(!s)return;
  for(const run of s.order){
    const chunks=s.chunks[run],received=chunks.reduce((n,c)=>n+(c.records?.length||0),0),total=s.settings.n;
    const box=el('div',undefined,'job'),head=el('div',undefined,'job-head');
    const state=s.active?'Running':s.details[run]?'Complete':anyFailed?'Needs attention':anyPending?'Paused':'Stopped';
    head.append(el('h2','AI generation: '+Research.runLabel(run).replace('_R0001','')),el('span',state,'tag '+(s.active?'tag-live':s.details[run]?'tag-done':anyFailed?'tag-error':'')));
    const progress=el('progress');progress.max=total;progress.value=received;progress.setAttribute('aria-label','Participants received');
    box.append(head,progress,el('p',`${received} of ${total} participants received`,'help'),el('p',s.message||'Results are held only in this browser tab.'));
    if(chunks.length>1||chunks.some(c=>c.error||c.notes.length))box.append(batchList(s,run));
    if(!s.details[run]&&received){const partial=el('button','Download participants received so far (partial CSV)');partial.type='button';partial.className='link';partial.addEventListener('click',()=>saveBlob(new Blob([csvText(chunks.filter(c=>c.records).flatMap(c=>c.records).sort((a,b)=>a.participant_id-b.participant_id))],{type:'text/csv'}),Research.runLabel(run)+'_partial.csv'));const row=el('div',undefined,'link-row');row.append(partial);box.append(row)}
    if(s.cleanupFailed)box.append(el('p','Immediate cleanup of a provider response could not be confirmed. OpenAI’s retention rules still apply.','help'));
    $('jobDetail').append(box);
  }
  for(const [run,d] of Object.entries(s.details)){
    const card=el('div',undefined,'job dataset'),top=el('div',undefined,'job-head');
    top.append(el('h2',Research.runLabel(run)),el('span',d.count+' participants','tag'));
    card.append(top,el('p',run.startsWith('SPA8_')?'Observed demographic and psychological predictors are kept, and the AI generated the outcomes.':'Inspect the generated score distributions and relationships before using this dataset to plan human research.'));
    const links=el('div',undefined,'link-row'),cb=el('button','Codebook only (CSV)'),dl=el('button','Dataset only (CSV)');
    cb.type=dl.type='button';cb.className=dl.className='link';
    cb.addEventListener('click',()=>saveBlob(new Blob([d.codebook_csv],{type:'text/csv;charset=utf-8'}),'codebook.csv'));
    dl.addEventListener('click',()=>saveBlob(new Blob([d.csv],{type:'text/csv'}),Research.runLabel(run)+'.csv'));
    links.append(dl,cb);card.append(links);
    const q=d.quality,flags=el('dl',undefined,'flags');
    [['Repeated complete profiles',q.repeated_complete_profiles],['Repeated baseline profiles',q.repeated_baseline_profiles],['Pilot-record matches',q.pilot_record_matches]].forEach(([k,v])=>{const w=el('div');w.append(el('dt',k),el('dd',String(v)));flags.append(w)});
    card.append(flags,el('p','Duplicates are kept and flagged.','help'));
    const notes=[...(d.warnings||[]),...s.chunks[run].filter(c=>c.quality).map(c=>c.quality)];
    if(notes.length){const w=el('div',undefined,'dataset-warnings');w.append(el('h3',`Quality notes (${notes.length})`),warningList(notes));card.append(w)}
    const preview=el('details',undefined,'note'),target=el('div');preview.append(el('summary','Preview the first 10 participants'));table(d.preview,target);
    preview.append(target,el('p','Readable labels are shown here. CSV downloads use the column names listed in the codebook.','help'));
    const dictionary=el('details',undefined,'note'),book=el('div');dictionary.append(el('summary','Codebook: variable names, definitions and scoring'));table(d.codebook,book);dictionary.append(book);
    card.append(preview,dictionary);$('datasetList').append(card);
  }
}

let evidenceData=null;
async function evidencePayload(){return evidenceData||(evidenceData=await api('/api/evidence'))}
async function evidence(){if(!$('evidenceResults').children.length){const data=await evidencePayload();StudyCharts.render(data.charts);tables(data,$('evidenceResults'))}}

async function init(){
  cfg=await api('/api/config');
  $('intro').textContent=cfg.intro;
  options($('n'),{'100':'100 participants'});
  table(cfg.variable_guide,$('guideTable'));
  $('serviceEstimate').textContent=cfg.service.estimated_minutes!=='60'?`The team's current planning estimate is ${cfg.service.estimated_minutes} minutes.`:'';
  $('serviceFunding').textContent=cfg.service.funding;$('serviceFuture').textContent=cfg.service.future;$('serviceContact').textContent=cfg.service.contact.text;
  Object.entries(cfg.terms).forEach(([title,text])=>{const d=el('details');d.append(el('summary',title),el('p',text));$('terms').append(d)});
  Object.values(cfg.metrics).forEach(([title,meaning,formula])=>{const d=el('details');d.append(el('summary',title),el('p',meaning),el('p',formula,'subtle'));$('metricGuide').append(d)});
  document.querySelectorAll('#nav button').forEach(b=>b.addEventListener('click',()=>page(b.dataset.page)));
  document.querySelectorAll('[data-goto]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();page(b.dataset.goto)}));
  $('reviewInputs').addEventListener('click',action(reviewInputs));
  ['seed','population','consent','sensitiveAck'].forEach(id=>$(id).addEventListener('input',invalidateReview));
  $('generate').addEventListener('click',action(start));
  $('checkAgain').addEventListener('click',action(drive));
  $('retryRun').addEventListener('click',action(retryFailed));
  $('stopRun').addEventListener('click',action(cancelRun));
  $('downloadAll').addEventListener('click',downloadAll);
  $('clearResults').addEventListener('click',action(discard));
  window.addEventListener('beforeunload',e=>{if(session){e.preventDefault();e.returnValue=''}});
  $('statusDot').classList.toggle('on',!!cfg.configured);
  $('accountLabel').textContent=cfg.configured?'AI generation available':'AI generation not connected';
  $('notConnected').hidden=!!cfg.configured;
  if(!cfg.configured)$('generate').disabled=true;
  Research.init();render();Console.init();
}
action(init)();
