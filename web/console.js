'use strict';
// Research console (design B): side navigation with step statuses, an inspector with the current
// selections, evidence and an activity log, and the full study results table on the approach page.
// Reads state owned by app.js and research.js. Owns only the table filter and the log.
const Console=(()=>{
 let tab='all',results=null,last={},logItems=[];
 const spa=()=>[...selected][0];
 const stage=()=>Research.situation();
 const complete=()=>session?Object.keys(session.details||{}).length:0;
 const studyLabel=()=>Research.custom()?(Research.study()?.title||'My own study'):'MIDUS demonstration';
 function dataLabel(){const m=spa();if(!m)return '';if(!uploadMap[m])return 'None needed';if(!Research.custom())return 'Example inputs supplied with the toolkit';
  const f=chosenFiles()[0]?.files[0];return f?f.name:Research.fictionalStudy()?'Fictional example data':'Not uploaded yet'}
 function status(){if(session)return complete()?`${complete()} dataset ready`:session.failed?'Needs attention':'Generating';return reviewedRequest?'Inputs checked, ready to generate':'Not started'}
 const metric=(k,w,m)=>results?.[`${k}_${w}`]?.[m];
 const f2=v=>v==null?'':v.toFixed(2),f3=v=>v==null?'':v.toFixed(3);
 function log(text){logItems.unshift([new Date().toLocaleTimeString('en-GB'),text]);logItems=logItems.slice(0,40);const box=$('activityLog');box.replaceChildren(...logItems.map(([t,x])=>{const d=el('div');d.append(el('time',t),document.createTextNode(x));return d}))}
 function track(){
  const now={goal:Research.goal(),stage:stage(),spa:spa(),study:Research.custom()?'own':'midus',checked:!!reviewedRequest,run:session?(complete()?'ready':session.failed?'attention':'running'):'none',compared:$('comparisonResults').children.length>0};
  if(now.goal&&now.goal!==last.goal)log('Goal: '+Research.goalTitle());
  if(now.stage&&now.stage!==last.stage)log('Situation: '+now.stage);
  if(now.spa&&now.spa!==last.spa&&now.goal&&now.stage)log('Approach: '+Research.methodLabel(now.spa));
  if(last.study&&now.study!==last.study)log('Study: '+studyLabel());
  if(now.checked&&!last.checked)log('Inputs checked');
  if(now.run!==last.run&&now.run!=='none')log({running:'Generation started',ready:'Dataset ready: 100 participants',attention:'Generation needs attention'}[now.run]);
  if(now.run==='none'&&last.run&&last.run!=='none')log('Session cleared');
  if(now.compared&&!last.compared)log('Comparison complete');
  last=now;
 }
 function nav(){
  const set=(id,text,ok)=>{const n=$(id);if(!n)return;n.textContent=text;n.classList.toggle('ok',!!ok)};
  set('navGoal',Research.goal()?'set':'to do',Research.goal());
  set('navSituation',stage()?'answered':'to do',stage());
  set('navApproach',spa()&&stage()?'SPA'+spa():'',spa()&&stage());
  set('navStudy',Research.custom()?'own':'MIDUS',true);
  set('navGenerate',session?'started':reviewedRequest?'checked':'',session||reviewedRequest);
  set('navDatasets',session?(complete()?'1 ready':session.failed?'attention':'running'):'none',complete());
  set('navCompare',$('comparisonResults').children.length?'done':'optional',$('comparisonResults').children.length);
 }
 function inspector(){
  const set=(id,text)=>{$(id).textContent=text||'Not chosen yet';$(id).classList.toggle('unset',!text)};
  set('selGoal',Research.goalTitle());set('selSituation',stage());set('selApproach',spa()&&stage()?Research.methodLabel(spa()):'');
  set('selStudy',studyLabel());set('selData',spa()&&stage()?dataLabel():'');$('selStatus').textContent=status();
  const m=spa(),box=$('inspEvidenceBox');box.hidden=!(m&&stage()&&results);
  if(!box.hidden){$('inspEvidenceTitle').textContent='Evidence for SPA'+m;
   $('inspScores').textContent=m===8?'Goal 1: keeps your supplied scores, so its score results describe your inputs.':`Goal 1: averages ${f2(metric('smd',0,m))} SD from human data. Distribution distance ${f2(metric('wasserstein',0,m))}.`;
   $('inspRelations').textContent=`Goal 2: correlation error ${f2(metric('correlation_mae',2,m))} at MIDUS 2 (lower is closer). Pattern r ${f2(metric('pattern_r',2,m))}.`}
 }
 function table(){
  const host=$('resultsTable');if(!results){host.replaceChildren(el('p','Loading the study results…','help'));return}
  const r=Research.recommendation(),fit=r&&stage()?r.feasible:[1,2,3,4,5,6,7,8],chosen=spa();
  const cols=[['smd',0,'|SMD|',true,'Average score difference, in standard deviations'],['wasserstein',0,'Distance',true,'Normalised Wasserstein distance between distributions'],['sd_ratio',0,'SD ratio',null,'Generated SD divided by human SD (1 is equal)'],['correlation_mae',2,'Error M2',true,'Correlation error with MIDUS 2 life satisfaction'],['correlation_mae',3,'Error M3',true,'Correlation error with MIDUS 3 life satisfaction'],['pattern_r',2,'Pattern r',false,'Pattern correlation at MIDUS 2'],['icc',2,'ICC',false,'Absolute agreement at MIDUS 2']];
  const best=(k,w,low)=>{const vals=[1,2,3,4,5,6,7].map(m=>metric(k,w,m));return low?Math.min(...vals):Math.max(...vals)};
  const t=el('table'),head=el('tr');['','Approach','Fits'].forEach(x=>head.append(el('th',x)));cols.forEach(c=>{const th=el('th',c[2]);th.title=c[4];th.setAttribute('scope','col');head.append(th)});const thead=el('thead');thead.append(head);t.append(thead);const body=el('tbody');
  for(const m of [1,2,3,4,5,6,7,8]){if(tab==='fit'&&!fit.includes(m))continue;
   const tr=el('tr');tr.className=[fit.includes(m)?'fit':'nofit',r&&stage()&&r.primary===m?'rec':''].join(' ');
   const pick=el('input');pick.type='radio';pick.name='consoleSpa';pick.checked=chosen===m&&!!stage();pick.disabled=!fit.includes(m)||!stage();pick.setAttribute('aria-label','Choose '+Research.methodLabel(m));
   pick.addEventListener('change',()=>{const card=document.querySelector(`input[name=chosenApproach][value="${m}"]`);if(card){card.checked=true;card.dispatchEvent(new Event('change'))}});
   const c0=el('td');c0.append(pick);const c1=el('td',Research.methodLabel(m));if(r&&stage()&&r.primary===m)c1.append(el('span','Recommended','tag tag-accent'));if(m===8)c1.append(el('sup','*'));
   tr.append(c0,c1,el('td',fit.includes(m)?'Yes':'No'));
   for(const [k,w,,low] of cols){const v=metric(k,w,m),td=el('td',f3(v));if(low!==null&&m!==8&&v===best(k,w,low))td.className='best';else if(low===true&&k==='correlation_mae'&&m===8)td.className='best';tr.append(td)}
   body.append(tr)}
  t.append(body);host.replaceChildren(t,el('p','Goal 1 columns: |SMD|, distance and SD ratio. Goal 2 columns: errors at MIDUS 2 and 3, pattern r and ICC. * SPA8 keeps the supplied psychological scores, so its Goal 1 columns describe its inputs. Hover over a heading for its meaning.','table-note'));
 }
 function refresh(){
  if(!cfg)return;track();nav();inspector();
  $('customPanel').hidden=!Research.custom();
  $('nextGoal').disabled=!Research.goal();
  $('nextSituation').disabled=!stage();
  const res=$('situationResult');res.hidden=!stage();if(stage())res.textContent='Your situation: '+stage()+'.';
  const ready=!!(Research.goal()&&stage()&&spa());$('approachNeeds').hidden=ready;
  $('confirmApproach').disabled=!ready;$('confirmApproach').textContent=ready?`Continue with SPA${spa()}`:'Continue with this approach';
  if(!$('approach').hidden)table();
 }
 async function load(){if(results)return;try{const d=await evidencePayload();results={};for(const r of d.charts.summary)(results[`${r.metric}_${r.wave}`]??={})[r.method]=r.mean;refresh();table()}catch(e){$('resultsTable').replaceChildren(el('p','The study results could not be loaded. They are also under Study findings.','help'))}}
 function shown(id){if(id==='approach'){table();load()}refresh()}
 function init(){
  document.querySelectorAll('#approach .tabs button').forEach(b=>b.addEventListener('click',()=>{tab=b.dataset.tab;document.querySelectorAll('#approach .tabs button').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-selected',x===b)});table()}));
  $('confirmApproach').addEventListener('click',()=>{if(!spa())return;inputs();page('study')});
  $('startOver').addEventListener('click',()=>{if(session&&!confirm('Start over? Datasets in this tab that you have not downloaded will be lost.'))return;session=null;location.reload()});
  const original=notice;notice=function(text,error){original(text,error);if(error&&text)log('Message: '+(typeof text==='string'?text:text.title||'Something went wrong'))};
  load();refresh();
 }
 return {init,refresh,shown};
})();
