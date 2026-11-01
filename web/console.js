'use strict';
// Research console (design B): side navigation with numbered, locked steps, an inspector with the current
// selections and an activity log, and the table of all eight approaches on the approach page.
// Step order: study, goal, questionnaire, information, approach, inputs (own study), check and generate, datasets.
// Reads state owned by app.js and research.js. Owns the step confirmations, the table filter and the log.
const Console=(()=>{
 let last={},logItems=[],studyChosen=false,confirmed=false,inputsDone=false,approachSeen=false;
 const spa=()=>[...selected][0];
 // The approach is shown in the inspector and log only once step 5 has been opened, so it does not appear before its explanation.
 const shownSpa=()=>approachSeen?spa():undefined;
 const stage=()=>Research.situation();
 const own=()=>Research.custom();
 const complete=()=>session?Object.keys(session.details||{}).length:0;
 const studyLabel=()=>!studyChosen?'':own()?(Research.study()?.title||'My own study'):'MIDUS demonstration';
 function steps(){return ['study','goal','questionnaire','situation','approach',...(own()?['inputs']:[]),'run','datasets']}
 function available(id){
  switch(id){
   case 'goal':return studyChosen;
   case 'questionnaire':return studyChosen&&!!Research.goal();
   case 'situation':return studyChosen&&!!Research.goal()&&Research.ready();
   case 'approach':return available('situation')&&!!stage();
   case 'inputs':return own()&&confirmed&&available('approach');
   case 'run':return confirmed&&available('approach')&&(!own()||inputsDone);
   case 'datasets':return !!session;
   default:return true;
  }
 }
 function dataLabel(){const m=spa();if(!m)return '';if(!uploadMap[m])return 'None needed';if(!own())return 'Example inputs supplied with the toolkit';
  const f=chosenFiles()[0]?.files[0];return f?f.name:'Not uploaded yet'}
 function status(){if(session)return complete()?`${complete()} dataset ready`:session.failed?'Needs attention':'Generating';return reviewedRequest?'Inputs checked, ready to generate':'Not started'}
 function log(text){logItems.unshift([new Date().toLocaleTimeString('en-GB'),text]);logItems=logItems.slice(0,40);const box=$('activityLog');box.replaceChildren(...logItems.map(([t,x])=>{const d=el('div');d.append(el('time',t),document.createTextNode(x));return d}))}
 function track(){
  if(last.stage!==undefined&&(stage()!==last.stage||Research.goal()!==last.goal||(own()?'own':'midus')!==last.study))approachSeen=false;
  const now={chosen:studyChosen,study:own()?'own':'midus',goal:Research.goal(),ready:Research.ready(),stage:stage(),spa:shownSpa(),checked:!!reviewedRequest,run:session?(complete()?'ready':session.failed?'attention':'running'):'none'};
  const changed=k=>last[k]!==undefined&&now[k]!==last[k];
  if(changed('study')||changed('goal')||changed('stage')||changed('spa')){confirmed=false;inputsDone=false}
  if(now.chosen&&(!last.chosen||changed('study')))log('Study: '+studyLabel());
  if(now.goal&&now.goal!==last.goal)log('Goal: '+Research.goalTitle());
  if(now.ready&&!last.ready)log(own()?'Questionnaire checked':'MIDUS measures chosen');
  if(now.stage&&now.stage!==last.stage)log('Information: '+now.stage);
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
  if(studyChosen){const n=own()?(Research.study()?.variables.length||0):0,[d,p]=own()?[0,0]:Research.midusCounts();q.textContent=!Research.ready()?(own()?'Not checked yet':'Not confirmed yet'):own()?`${n} measure${n===1?'':'s'} checked`:`${d} demographic${d===1?'':'s'}, ${p} predictor${p===1?'':'s'}`;q.classList.toggle('unset',!Research.ready())}
  set('selSituation',stage());set('selApproach',shownSpa()&&stage()?Research.methodLabel(spa()):'');
  set('selData',shownSpa()&&stage()?dataLabel():'');$('selStatus').textContent=status();
 }
 // All eight approaches with whether each fits the chosen information. Study results are under Study findings.
 function table(){
  const host=$('resultsTable'),r=Research.recommendation(),ready=!!(r&&stage()),fit=ready?r.feasible:[],chosen=spa();
  const t=el('table'),head=el('tr');['','Approach','Fits your information'].forEach(x=>{const th=el('th',x);th.setAttribute('scope','col');head.append(th)});const thead=el('thead');thead.append(head);t.append(thead);const body=el('tbody');
  for(const m of [1,2,3,4,5,6,7,8]){
   const ok=fit.includes(m),tr=el('tr');tr.className=[ok?'fit':'nofit',ready&&r.primary===m?'rec':''].join(' ');
   const pick=el('input');pick.type='radio';pick.name='consoleSpa';pick.checked=chosen===m&&ready;pick.disabled=!ok;pick.setAttribute('aria-label','Choose '+Research.methodLabel(m));
   pick.addEventListener('change',()=>{const card=document.querySelector(`input[name=chosenApproach][value="${m}"]`);if(card){card.checked=true;card.dispatchEvent(new Event('change'))}});
   const c0=el('td');c0.append(pick);const c1=el('td',Research.methodLabel(m));if(ready&&r.primary===m)c1.append(el('span','Recommended','tag tag-accent'));
   tr.append(c0,c1,el('td',!ready?'':ok?'Yes':'No'));body.append(tr)}
  t.append(body);host.replaceChildren(t,el('p','You can choose any approach that fits. Results for every approach are under Study findings.','table-note'));
 }
 function buttons(){
  $('nextStudy').disabled=!studyChosen;
  $('ownNext').hidden=!(studyChosen&&own());
  $('nextGoal').disabled=!Research.goal();$('nextGoal').textContent='Next: questionnaire';
  $('midusQuestionnaire').hidden=own();$('customPanel').hidden=!own();
  $('qTitle').textContent=own()?'Define your study and questionnaire':'Choose the MIDUS measures';
  $('qSub').textContent=own()?'Choose how to enter your variables: one by one on this page, or by uploading a CSV that lists them. Either way, you give the demographic characteristics, then the psychological measures with their definitions, sources, items and scoring. Participant data come later, when the approach needs them.':'Choose the demographic characteristics, then the psychological predictors to include. All are ticked to start with, as in the proposal.';
  $('confirmStudy').textContent='Continue';
  $('nextSituation').disabled=!stage();
  const res=$('situationResult');res.hidden=!stage();if(stage())res.textContent=(own()?'Your available information: ':'The simulation will use: ')+stage()+'.';
  $('infoTitle').textContent=own()?'What information can you provide?':'Which information should the simulation use?';
  $('infoSub').textContent=own()?'Different approaches use different information. Choose the one option that best describes what you have now.':'The MIDUS demonstration includes example information of every kind, so you can try each approach. Choose the information the simulation should use, and the recommended approach follows from it.';
  const ready=!!(Research.goal()&&stage()&&spa());$('approachNeeds').hidden=ready;
  $('confirmApproach').disabled=!ready;$('confirmApproach').textContent=ready?`Continue with SPA${spa()}`:'Continue with this approach';
  const midus=!own()&&!!spa();$('midusInputs').hidden=!midus;$('midusSetup').hidden=!(studyChosen&&!own());
  if(midus){$('midusInputText').textContent=$('dataSummary').textContent;const ex=$('midusExample');ex.hidden=$('exampleLink').hidden;ex.href=$('exampleFile').href;ex.download=$('exampleFile').download}
 }
 function refresh(){
  if(!cfg)return;track();nav();inspector();buttons();
  if(!$('approach').hidden)table();
 }
 function shown(id){if(id==='approach'){approachSeen=true;table()}refresh()}
 function init(){
  $('studyChoices').addEventListener('change',()=>{studyChosen=true;refresh()});
  $('nextGoal').addEventListener('click',()=>page('questionnaire'));
  $('confirmStudy').addEventListener('click',action(async()=>{if(own())await Research.checkDefinition();else Research.confirmMidus();refresh();page('situation')}));
  $('confirmApproach').addEventListener('click',()=>{if(!spa())return;inputs();confirmed=true;log('Confirmed '+Research.methodLabel(spa()));refresh();page(own()?'inputs':'run')});
  $('confirmInputs').addEventListener('click',()=>{inputsDone=true;log('Inputs ready');refresh();page('run')});
  $('startOver').addEventListener('click',()=>{if(session&&!confirm('Start over? Datasets in this tab that you have not downloaded will be lost.'))return;session=null;location.reload()});
  const original=notice;notice=function(text,error){original(text,error);if(error&&text)log('Message: '+(typeof text==='string'?text:text.title||'Something went wrong'))};
  refresh();
 }
 return {init,refresh,shown,available};
})();
