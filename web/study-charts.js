/* Original-study visualisations only. Uses verified aggregates, never session data. */
'use strict';
const StudyCharts=(()=>{
  const display=text=>String(text);
  const order=[1,2,3,4,5,6,7,8];
  const NS='http://www.w3.org/2000/svg';
  const short={1:'Persona prompted',2:'Direct generation',3:'Population guided',4:'Quota matched',5:'Pilot calibrated',6:'Pilot analysis guided',7:'Demographic-only profiles',8:'Demographics + psychology *'};
  const definitions={
    wasserstein:{axis:'Normalised Wasserstein distance · lower is closer',meaning:'Wasserstein distance compares the full score distributions, expressed in human standard deviations. Zero means identical distributions. Values are averaged across the 38 psychological predictors.'},
    smd:{axis:'Absolute standardised mean difference · lower is closer',meaning:'Standardised mean error measures gaps between simulated and human average scores relative to their pooled score variability. Zero means equal averages. Absolute errors are averaged across 38 predictors.'},
    sd_error:{axis:'Absolute SD-ratio error · lower is closer',meaning:'The standard deviation (SD) describes variation between people. This measure averages the absolute gaps between the simulated-to-human SD ratio and its target of 1. Zero means equal variability for all 38 predictors.'}
  };
  const series=[{metric:'pattern_r',name:'Pearson pattern r',color:'#815397',dy:-9},{metric:'icc',name:'ICC(A,1)',color:'#245f86',dy:0},{metric:'ccc',name:'Lin’s CCC',color:'#257e73',dy:9}];
  let source=null;
  const fmt=x=>Number.isFinite(x)?x.toFixed(4):'Not available';
  function dataFor(data,metric,wave){
    const rows=data.summary.filter(r=>r.metric===metric&&r.wave===Number(wave)).slice().sort((a,b)=>a.method-b.method);
    if(rows.length!==8||rows.some((r,i)=>r.method!==i+1||![r.mean,r.lower,r.upper].every(Number.isFinite)||r.lower>r.mean||r.upper<r.mean))throw Error('The original-study chart data are incomplete. Use the detailed results table.');
    return rows;
  }
  function scatterFor(data,method,wave){
    const humans=new Map(data.human.map(h=>[h.code,h]));
    const rows=data.variables.filter(r=>r.method===Number(method)&&r.code!=='anxiety_symptoms').map(r=>{
      const h=humans.get(r.code);
      return {code:r.code,label:data.variable_labels[r.code]||r.code,human:h?.[`midus${wave}_r`],generated:r[`midus${wave}_mean_r`],mae:r[`midus${wave}_mae`],n:r[`midus${wave}_runs`]};
    });
    if(rows.length!==37||rows.some(r=>!Number.isFinite(r.human)||!Number.isFinite(r.generated)||Math.abs(r.human)>1||Math.abs(r.generated)>1))throw Error('The variable-level study data are incomplete. Use the detailed results table.');
    return rows;
  }
  function intervalSpec(rows,unit=false){
    const high=Math.max(...rows.map(r=>r.upper)),step=unit ? .2 : (high<=.36 ? .1 : .2),max=unit ? 1 : Math.ceil(high*1.1/step)*step;
    return {min:0,max,step,width:1000,height:430,left:282,right:78,top:30,row:39,bottom:356};
  }
  function node(tag,attrs={},text){const e=document.createElementNS(NS,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,display(v)));if(text!==undefined)e.textContent=display(text);return e}
  function html(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=display(text);if(cls)e.className=cls;return e}
  function base(target,title,desc,width=1000,height=430){
    const svg=node('svg',{viewBox:`0 0 ${width} ${height}`,role:'group','aria-label':title,class:'study-svg'});
    svg.append(node('title',{},title),node('desc',{},desc));document.getElementById(target).replaceChildren(svg);return svg;
  }
  function text(svg,x,y,label,attrs={}){svg.append(node('text',{x,y,fill:'#344e58','font-size':14,...attrs},label))}
  function interactive(element,description,target){
    element.setAttribute('tabindex','0');element.setAttribute('role','img');element.setAttribute('aria-label',display(description));element.append(node('title',{},description));
    for(const event of ['pointerenter','focus'])element.addEventListener(event,()=>{document.getElementById(target).textContent=display(description)});
  }
  function rowColor(m){return m===5?'#257e73':m===6?'#4267a9':m===8?'#a5672a':'#6f8793'}
  function whisker(svg,x,low,high,y,color){
    svg.append(node('line',{x1:x(low),x2:x(high),y1:y,y2:y,stroke:color,'stroke-width':2.5}),node('line',{x1:x(low),x2:x(low),y1:y-5,y2:y+5,stroke:color,'stroke-width':1.5}),node('line',{x1:x(high),x2:x(high),y1:y-5,y2:y+5,stroke:color,'stroke-width':1.5}));
  }
  function axis(svg,spec,label){
    const x=v=>spec.left+(v-spec.min)/(spec.max-spec.min)*(spec.width-spec.left-spec.right);
    const ticks=Math.round((spec.max-spec.min)/spec.step);
    for(let i=0;i<=ticks;i++){
      const value=spec.min+(spec.max-spec.min)*i/ticks,p=x(value);
      svg.append(node('line',{x1:p,x2:p,y1:12,y2:spec.bottom,stroke:'#dce5e5','stroke-width':1}));
      text(svg,p,spec.bottom+25,Math.abs(value)<1e-10?'0':value.toFixed(2),{'text-anchor':'middle','font-size':13});
    }
    text(svg,(spec.left+spec.width-spec.right)/2,spec.bottom+59,label,{'text-anchor':'middle','font-size':14});
    return x;
  }
  function pointDescription(r,label){return `SPA${r.method} ${source.method_names[r.method]}. ${label}: ${fmt(r.mean)}. 95% CI ${fmt(r.lower)} to ${fmt(r.upper)}. ${r.n} scored repetitions.${r.method===8?' Actual psychological predictors are retained.':''}`}
  function intervalChart(target,rows,axisLabel,readout,highlight){
    const spec=intervalSpec(rows),svg=base(target,axisLabel,'Eight approaches, each shown by a mean point and a 95% confidence interval. Lower error means closer reproduction of human data. SPA8 retains actual psychological predictors.');
    const x=axis(svg,spec,axisLabel);text(svg,990,8,'Mean / 95% CI',{'text-anchor':'end','font-size':11});
    rows.slice().sort((a,b)=>order.indexOf(a.method)-order.indexOf(b.method)).forEach((r,i)=>{
      const y=spec.top+i*spec.row;
      if(r.method===highlight||r.method===8)svg.append(node('rect',{x:3,y:y-18,width:990,height:36,rx:5,fill:r.method===8?'#f8f1e7':'#edf4f1'}));
      text(svg,12,y+5,`SPA${r.method}  ${short[r.method]}`,{'font-weight':r.method===highlight||r.method===8?650:400});
      const color=rowColor(r.method);whisker(svg,x,r.lower,r.upper,y,color);
      const dot=node('circle',{cx:x(r.mean),cy:y,r:5,fill:r.method===8?'white':color,stroke:color,'stroke-width':2.5});
      interactive(dot,pointDescription(r,axisLabel),readout);svg.append(dot);
      text(svg,990,y+1,fmt(r.mean),{'text-anchor':'end','font-weight':600});
      text(svg,990,y+15,`${fmt(r.lower)}–${fmt(r.upper)}`,{'text-anchor':'end','font-size':10,fill:'#60757c'});
    });
    document.getElementById(readout).textContent=pointDescription(rows.find(r=>r.method===highlight),axisLabel);
  }
  function agreementChart(wave){
    const rows=series.flatMap(s=>dataFor(source,s.metric,wave));const spec=intervalSpec(rows,true),svg=base('agreementChart','Pattern similarity and numerical agreement','Pearson pattern correlation, ICC(A,1) and Lin’s CCC across eight approaches. Means and 95% confidence intervals use a common zero-to-one scale. Target: one.');
    const x=axis(svg,spec,'Mean agreement or pattern correlation · target = 1');
    svg.append(node('line',{x1:x(1),x2:x(1),y1:12,y2:spec.bottom,stroke:'#637a82','stroke-width':1.6,'stroke-dasharray':'5 4'}));
    const legend=document.getElementById('agreementLegend');legend.replaceChildren();
    for(const s of series){const item=html('span',undefined,'study-series');const swatch=html('span',undefined,`study-swatch metric-${s.metric}`);item.append(swatch,document.createTextNode(s.name));legend.append(item)}
    for(const m of order){
      const y=spec.top+order.indexOf(m)*spec.row;text(svg,12,y+5,`SPA${m}  ${short[m]}`,{'font-weight':m===8?650:400});
      for(const s of series){
        const r=dataFor(source,s.metric,wave).find(r=>r.method===m);whisker(svg,x,r.lower,r.upper,y+s.dy,s.color);
        const dot=node('circle',{cx:x(r.mean),cy:y+s.dy,r:4.6,fill:m===8?'white':s.color,stroke:s.color,'stroke-width':2});
        interactive(dot,pointDescription(r,s.name),'agreementReadout');svg.append(dot);
      }
    }
    const sample=dataFor(source,'pattern_r',wave).find(r=>r.method===5),icc=dataFor(source,'icc',wave).find(r=>r.method===5);
    document.getElementById('agreementReadout').textContent=`For SPA5, Pearson pattern r is ${fmt(sample.mean)}, while ICC(A,1) is ${fmt(icc.mean)} at MIDUS ${wave}. High pattern similarity coexists with lower numerical agreement.`;
  }
  function scatterChart(wave){
    const method=Number(document.getElementById('studyScatterMethod').value),rows=scatterFor(source,method,wave);
    const W=800,H=610,L=91,R=38,T=25,B=88,plot=Math.min(W-L-R,H-T-B),x=v=>L+(v+1)/2*plot,y=v=>T+(1-v)/2*plot;
    const svg=base('correlationChart',`SPA${method} psychological correlations at MIDUS ${wave}`,'One point per psychological predictor. Horizontal: observed human correlation. Vertical: average generated correlation. The diagonal represents exact numerical agreement.',W,H);
    for(const t of [-1,-.5,0,.5,1]){
      svg.append(node('line',{x1:x(t),x2:x(t),y1:y(1),y2:y(-1),stroke:t===0?'#aebfc3':'#e1e8e7'}),node('line',{x1:x(-1),x2:x(1),y1:y(t),y2:y(t),stroke:t===0?'#aebfc3':'#e1e8e7'}));
      text(svg,x(t),y(-1)+25,t.toFixed(1),{'text-anchor':'middle'});text(svg,L-15,y(t)+5,t.toFixed(1),{'text-anchor':'end'});
    }
    svg.append(node('line',{x1:x(-1),x2:x(1),y1:y(-1),y2:y(1),stroke:'#8a7764','stroke-width':2,'stroke-dasharray':'7 5'}));
    text(svg,L+plot+20,T+18,'Equal values',{'font-size':13});
    text(svg,L+plot/2,y(-1)+62,'Human correlation with life satisfaction',{'text-anchor':'middle','font-size':16});
    svg.append(node('text',{x:23,y:T+plot/2,transform:`rotate(-90 23 ${T+plot/2})`,'text-anchor':'middle',fill:'#344e58','font-size':16},'Average simulated correlation with life satisfaction'));
    for(const r of rows){
      const dot=node('circle',{cx:x(r.human),cy:y(r.generated),r:5.6,fill:method===8?'white':rowColor(method),stroke:rowColor(method),'stroke-width':2,opacity:.85});
      interactive(dot,`${r.label}. Human correlation ${fmt(r.human)}. Average simulated correlation ${fmt(r.generated)}. Mean absolute correlation error ${fmt(r.mae)}. ${r.n} available repetitions.`,'correlationReadout');svg.append(dot);
    }
    document.getElementById('correlationReadout').textContent=display(`SPA${method} ${source.method_names[method]} at MIDUS ${wave}. Inspect a point to see the psychological variable and its values. Points closer to the diagonal have closer average correlation values.`);
  }
  function takeaway(title,value,measure,explanation,cls){const card=html('div',undefined,'study-takeaway '+cls);card.append(html('h2',title),html('div',value,'study-big-value'),html('p',measure,'study-measure'),html('p',explanation));return card}
  function update(){
    const wave=Number(document.getElementById('studyWave').value),metric=document.getElementById('studyDistribution').value;
    const distributions=dataFor(source,metric,0),water=dataFor(source,'wasserstein',0),relationships=dataFor(source,'correlation_mae',wave);
    const get=(rows,m)=>rows.find(r=>r.method===m),m5=get(water,5),m6=get(relationships,6),m8=get(relationships,8);
    document.getElementById('studyTakeaways').replaceChildren(
      takeaway('SPA5 · Closest generated score distributions',fmt(m5.mean),'Normalised Wasserstein distance','The lowest distribution error among approaches that generate psychological scores.','takeaway-m5'),
      takeaway('SPA6 · Closest relationships from generated scores',fmt(m6.mean),`Correlation error · MIDUS ${wave}`,'The lowest relationship error among approaches that generate psychological scores.','takeaway-m6'),
      takeaway('SPA8 · Closest relationships overall',fmt(m8.mean),`Correlation error · MIDUS ${wave}`,'Actual demographics and psychological predictors are supplied, and the model generates the outcomes.','takeaway-spa8'));
    document.getElementById('distributionMeaning').textContent=definitions[metric].meaning;
    intervalChart('distributionChart',distributions,definitions[metric].axis,'distributionReadout',5);
    const worst=distributions.filter(r=>r.method!==8).reduce((a,b)=>a.mean>b.mean?a:b);
    document.getElementById('distributionFinding').textContent=`SPA5 has the smallest error among approaches that generate psychological scores (${fmt(get(distributions,5).mean)}). SPA${worst.method} has the largest error for this measure (${fmt(worst.mean)}). SPA8’s low error (${fmt(get(distributions,8).mean)}) reflects its use of actual psychological scores.`;
    intervalChart('relationshipChart',relationships,`Correlation mean absolute error at MIDUS ${wave} · lower is closer`,'relationshipReadout',6);
    document.getElementById('relationshipFinding').textContent=`SPA6 has lower relationship error (${fmt(m6.mean)}) than SPA5 (${fmt(get(relationships,5).mean)}) among approaches generating psychological scores. SPA8 is closest overall (${fmt(m8.mean)}) while retaining actual predictors. SPA7’s error remains ${fmt(get(relationships,7).mean)} despite using actual demographic profiles.`;
    agreementChart(wave);scatterChart(wave);for(const id of ['distributionReadout','distributionFinding','relationshipReadout','relationshipFinding','agreementReadout','correlationReadout']){const e=document.getElementById(id);e.textContent=display(e.textContent)}
  }
  function render(data){
    source=data;const select=document.getElementById('studyScatterMethod');select.replaceChildren();
    for(const m of order){const option=html('option',`SPA${m} · ${data.method_names[m]}`);option.value=m;select.append(option)}select.value='5';
    for(const id of ['studyWave','studyDistribution','studyScatterMethod'])document.getElementById(id).onchange=update;
    const guide=document.getElementById('studyMethodGuide');guide.replaceChildren();
    const table=html('table'),head=html('tr');['Approach','Information supplied'].forEach(t=>head.append(html('th',t)));const thead=html('thead');thead.append(head);table.append(thead);const tbody=html('tbody');
    const inputs={1:'Definitions and an instruction to imagine a different person for each row.',2:'Definitions and an instruction to generate records directly.',3:'Definitions plus qualitative population guidance.',4:'Constructed demographic profiles matching marginal proportions.',5:'50 pilot records plus precomputed statistical summaries.',6:'50 pilot records, which the model is instructed to analyse itself.',7:'Actual demographic profiles, kept fixed.',8:'Actual demographic and psychological profiles, kept fixed.'};
    for(const m of order){const row=html('tr');row.append(html('td',`SPA${m} · ${data.method_names[m]}`),html('td',inputs[m]));tbody.append(row)}table.append(tbody);guide.append(table);update();
  }
  return {render,dataFor,scatterFor,intervalSpec};
})();
