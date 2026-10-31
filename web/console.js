'use strict';
// Research console (design B): side navigation with numbered, locked steps, an inspector with the current
// selections, evidence and an activity log, and the full study results table on the approach page.
// Step order: study, goal, questionnaire (own study), situation, approach, inputs (own study), check and generate, datasets.
// Reads state owned by app.js and research.js. Owns the step confirmations, the table filter and the log.
const Console=(()=>{
 let tab='all',results=null,last={},logItems=[],studyChosen=false,confirmed=false,inputsDone=false;
 const spa=()=>[...selected][0];
 const stage=()=>Research.situation();
 const own=()=>Research.custom();
 const complete=()=>session?Object.keys(session.details||{}).length:0;
 const studyLabel=()=>!studyChosen?'':own()?(Research.study()?.title||'My own study'):'MIDUS demonstration';
 function steps(){return ['study','goal',...(own()?['questionnaire']:[]),'situation','approach',...(own()?['inputs']:[]),'run','datasets']}
 function available(id){
  switch(id){
   case 'goal':return studyChosen;
   case 'questionnaire':return studyChosen&&own()&&!!Research.goal();
   case 'situation':return studyChosen&&!!Research.goal()&&(!own()||Research.ready());
   case 'approach':return available('situation')&&!!stage();
   case 'inputs':return own()&&confirmed&&available('approach');
   case 'run':return confirmed&&available('approach')&&(!own()||inputsDone);
   case 'datasets':return !!session;
   default:return true;
  }
 }
 function dataLabel(){const m=spa();if(!m)return '';if(!uploadMap[m])return 'None needed';if(!own())return 'Example inputs supplied with the toolkit';
  const f=chosenFiles()[0]?.files[0];return f?f.name:Research.fictionalStudy()?'Fictional example data':'Not uploaded yet'}
 function status(){if(session)return complete()?`${complete()} dataset ready`:session.failed?'Needs attention':'Generating';return reviewedRequest?'Inputs checked, ready to generate':'Not started'}
 const metric=(k,w,m)=>results?.[`${k}_${w}`]?.[m];
 const f2=v=>v==null?'':v.toFixed(2),f3=v=>v==null?'':v.toFixed(3);
 function log(text){logItems.unshift([new Date().toLocaleTimeString('en-GB'),text]);logItems=logItems.slice(0,40);const box=$('activityLog');box.replaceChildren(...logItems.map(([t,x])=>{const d=el('div');d.append(el('time',t),document.createTextNode(x));return d}))}
 function track(){
  const now={chosen:studyChosen,study:own()?'own':'midus',goal:Research.goal(),ready:own()&&Research.ready(),stage:stage(),spa:spa(),checked:!!reviewedRequest,run:session?(complete()?'ready':session.failed?'attention':'running'):'none'};
  const changed=k=>last[k]!==undefined&&now[k]!==last[k];
  if(changed('study')||changed('goal')||changed('stage')||changed('spa')){confirmed=false;inputsDone=false}
  if(now.chosen&&(!last.chosen||changed('study')))log('Study: '+studyLabel());
  if(now.goal&&now.goal!==last.goal)log('Goal: '+Research.goalTitle());
  if(now.ready&&!last.ready)log('Questionnaire checked');
  if(now.stage&&now.stage!==last.stage)log('Situation: '+now.stage);
  if(now.spa&&now.spa!==last.spa&&now.goal&&now.stage)log('Approach: '+Research.methodLabel(now.spa));
  if(now.checked&&!last.checked)log('Inputs checked');
  if(now.run!==last.run&&now.run!=='none')log({running:'Generation started',ready:'Dataset ready: 100 participants',attention:'Generation needs attention'}[now.run]);
  if(now.run==='none'&&last.run&&last.run!=='none')log('Session cleared');
  last=now;
 }
 function nav(){
  const order=steps();
  document.querySelectorAll('#nav button[data-step]').forEach(b=>{
   const id=b.dataset.page,n=order.indexOf(id);b.hidden=n<0;if(n<0)return;
   b.querySelector('.step-no').textContent=(n+1)+' ';
   const open=available(id);b.disabled=!open;b.title=open?'':'Complete the earlier steps first';
  });
  document.querySelectorAll('[data-crumb]').forEach(c=>{const n=order.indexOf(c.dataset.crumb);c.textContent=n<0?'Workflow':'Workflow / '+(n+1)});
  const set=(id,text,ok)=>{const node=$(id);if(!node)return;const open=available(node.closest('button').dataset.page);node.textContent=open?text:'locked';node.classList.toggle('ok',open&&!!ok)};
  const done=(id,ok)=>set(id,ok?'completed':'to do',ok);
  done('navStudy',studyChosen);done('navGoal',!!Research.goal());done('navQuestionnaire',Research.ready());done('navSituation',!!stage());
  done('navApproach',confirmed);done('navInputs',inputsDone);done('navGenerate',!!session);
  set('navDatasets',complete()?'completed':session?.failed?'attention':session?'running':'to do',complete());
 }
 function inspector(){
  const set=(id,text)=>{$(id).textContent=text||'Not chosen yet';$(id).classList.toggle('unset',!text)};
  set('selStudy',studyLabel());set('selGoal',Research.goalTitle());
  const q=$('selQuestionnaire');q.hidden=$('selQuestionnaireLabel').hidden=!studyChosen;
  if(studyChosen){const n=own()?(Research.study()?.variables.length||0):0;q.textContent=!own()?'MIDUS measures provided':Research.ready()?`${n} measure${n===1?'':'s'} checked`:'Not checked yet';q.classList.toggle('unset',own()&&!Research.ready())}
  set('selSituation',stage());set('selApproach',spa()&&stage()?Research.methodLabel(spa()):'');
  set('selData',spa()&&stage()?dataLabel():'');$('selStatus').textContent=status();
  const m=spa(),box=$('inspEvidenceBox');box.hidden=!(m&&stage()&&results);
  if(!box.hidden){$('inspEvidenceTitle').textContent='Evidence for SPA'+m;
   $('inspScores').textContent=m===8?'Goal 1: keeps your supplied scores, so its score results describe your inputs.':`Goal 1: averages ${f2(metric('smd',0,m))} SD from human data. Distribution distance ${f2(metric('wasserstein',0,m))}.`;
   $('inspRelations').textContent=`Goal 2: correlation error ${f2(metric('correlation_mae',2,m))} at MIDUS 2 (lower is closer). Pattern r ${f2(metric('pattern_r',2,m))}.`}
 }
 function table(){
  const host=$('resultsTable');if(!results){host.replaceChildren(el('p','Loading the study results…','help'));return}
  const r=Research.recommendation(),fit=r&&stage()?r.feasible:[1,2,3,4,5,6,7,8],chosen=spa();
  const cols=[['smd',0,'|SMD|',true,'Average score difference, in standard deviations'],['wasserstein',0,'Distance',true,'Normalised Wasserstein distance between distributions'],['sd_ratio',0,'SD ratio',null,'Generated SD divided by human SD (1 is equal)'],['correlation_mae',2,'Error, MIDUS 2',true,'Correlation error with MIDUS 2 life satisfaction'],['correlation_mae',3,'Error, MIDUS 3',true,'Correlation error with MIDUS 3 life satisfaction'],['pattern_r',2,'Pattern r',false,'Pattern correlation at MIDUS 2'],['icc',2,'ICC',false,'Absolute agreement at MIDUS 2']];
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
 function buttons(){
  $('nextStudy').disabled=!studyChosen;
  $('ownNext').hidden=!(studyChosen&&own());
  $('nextGoal').disabled=!Research.goal();$('nextGoal').textContent=own()?'Next: define your questionnaire':'Next: your situation';
  $('nextSituation').disabled=!stage();
  const res=$('situationResult');res.hidden=!stage();if(stage())res.textContent='Your situation: '+stage()+'.';
  const ready=!!(Research.goal()&&stage()&&spa());$('approachNeeds').hidden=ready;
  $('confirmApproach').disabled=!ready;$('confirmApproach').textContent=ready?`Continue with SPA${spa()}`:'Continue with this approach';
  const midus=!own()&&!!spa();$('midusInputs').hidden=!midus;$('midusSetup').hidden=!(studyChosen&&!own());
  if(midus){$('midusInputText').textContent=$('dataSummary').textContent;const ex=$('midusExample');ex.hidden=$('exampleLink').hidden;ex.href=$('exampleFile').href;ex.download=$('exampleFile').download}
 }
 function refresh(){
  if(!cfg)return;track();nav();inspector();buttons();
  if(!$('approach').hidden)table();
 }
 async function load(){if(results)return;try{const d=await evidencePayload();results={};for(const r of d.charts.summary)(results[`${r.metric}_${r.wave}`]??={})[r.method]=r.mean;refresh();table()}catch(e){$('resultsTable').replaceChildren(el('p','The study results could not be loaded. They are also under Study findings.','help'))}}
 function shown(id){if(id==='approach'){table();load()}refresh()}
 function init(){
  document.querySelectorAll('#approach .tabs button').forEach(b=>b.addEventListener('click',()=>{tab=b.dataset.tab;document.querySelectorAll('#approach .tabs button').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-selected',x===b)});table()}));
  $('studyChoices').addEventListener('change',()=>{studyChosen=true;refresh()});
  $('nextGoal').addEventListener('click',()=>page(own()?'questionnaire':'situation'));
  $('confirmStudy').addEventListener('click',action(async()=>{await Research.checkDefinition();refresh();page('situation')}));
  $('confirmApproach').addEventListener('click',()=>{if(!spa())return;inputs();confirmed=true;log('Confirmed '+Research.methodLabel(spa()));refresh();page(own()?'inputs':'run')});
  $('confirmInputs').addEventListener('click',()=>{inputsDone=true;log('Inputs ready');refresh();page('run')});
  $('startOver').addEventListener('click',()=>{if(session&&!confirm('Start over? Datasets in this tab that you have not downloaded will be lost.'))return;session=null;location.reload()});
  const original=notice;notice=function(text,error){original(text,error);if(error&&text)log('Message: '+(typeof text==='string'?text:text.title||'Something went wrong'))};
  load();refresh();
 }
 return {init,refresh,shown,available};
})();
