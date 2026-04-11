/* result.js — Netlify version */
'use strict';

const API_BASE = 'https://mediai-esbq.onrender.com';

function fmt(s){ return (s||'').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase()); }

async function loadResult(){
  const symptoms = JSON.parse(sessionStorage.getItem('mediai_symptoms') || '[]');
  if(!symptoms.length){
    document.getElementById('resLoading').innerHTML = `
      <div style="text-align:center;padding:40px">
        <p style="color:var(--text2);margin-bottom:16px">No symptoms found. Please go back and select symptoms.</p>
        <a class="btn-primary" href="/diagnose" style="display:inline-block;background:var(--teal);color:#000;padding:12px 24px;border-radius:12px;font-weight:500">← Go to Diagnosis</a>
      </div>`;
    return;
  }

  try{
    const res = await fetch(API_BASE + '/api/predict',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({symptoms, top_k:5})
    });
    if(!res.ok) throw new Error('API error');
    const data = await res.json();
    if(data.error) throw new Error(data.error);
    renderResult(data);
  } catch(e){
    renderFallback(symptoms);
  }
}

function renderResult(data){
  document.getElementById('resLoading').style.display = 'none';
  document.getElementById('resCard').style.display    = 'block';
  document.getElementById('precPanel').style.display  = 'block';

  const risk = (data.risk_level||'Low').toLowerCase();
  const riskEl = document.getElementById('resRisk');
  riskEl.textContent = (data.risk_level||'Low').toUpperCase() + ' RISK';
  riskEl.className = 'res-risk-badge ' + risk;

  document.getElementById('resDisease').textContent = data.primary_disease;

  const conf = parseFloat(data.confidence)||0;
  document.getElementById('resConf').textContent = conf.toFixed(1) + '%';
  setTimeout(()=>{ document.getElementById('resBar').style.width = conf + '%'; }, 80);

  const t5 = document.getElementById('resTop5');
  t5.innerHTML = '';
  (data.top_predictions||[]).forEach(([name,pct],i)=>{
    t5.insertAdjacentHTML('beforeend',`
      <div class="res-pred-row">
        <span class="res-pred-name">${name}</span>
        <div class="res-pred-track"><div class="res-pred-fill ${i===0?'first':'other'}" style="width:0%" data-w="${pct}"></div></div>
        <span class="res-pred-pct">${pct.toFixed(1)}%</span>
      </div>`);
  });
  setTimeout(()=>{
    document.querySelectorAll('.res-pred-fill[data-w]').forEach(el=>{
      el.style.width = el.dataset.w + '%';
    });
  },100);

  const sc = document.getElementById('resSyms');
  if(sc) sc.innerHTML = (data.symptoms_used||[]).map(s=>`<span class="res-sym-chip">${fmt(s)}</span>`).join('');

  renderPrecautions(data.primary_disease);
}

function renderPrecautions(diseaseName){
  const prec = window.PRECAUTIONS && window.PRECAUTIONS[diseaseName];
  const nameEl = document.getElementById('precDisease');
  if(nameEl) nameEl.textContent = diseaseName;

  if(!prec){
    const panel = document.getElementById('precPanel');
    if(panel) panel.innerHTML = `
      <div class="prec-header">
        <svg viewBox="0 0 24 24" fill="none" width="18" height="18"><path d="M12 2L3 7v5c0 5.5 4 10.7 9 12 5-1.3 9-6.5 9-12V7L12 2z" stroke="currentColor" stroke-width="1.5"/></svg>
        Precautions for ${diseaseName}
      </div>
      <p style="font-size:.875rem;color:var(--text2);line-height:1.7;margin-top:12px">
        Please consult a qualified healthcare professional for specific advice on <strong>${diseaseName}</strong>.
      </p>`;
    return;
  }
  const doEl    = document.getElementById('precDoList');
  const avoidEl = document.getElementById('precAvoidList');
  const emergEl = document.getElementById('precEmergList');
  if(doEl)    doEl.innerHTML    = prec.do.map(i=>`<li>${i}</li>`).join('');
  if(avoidEl) avoidEl.innerHTML = prec.avoid.map(i=>`<li>${i}</li>`).join('');
  if(emergEl) emergEl.innerHTML = prec.emergency.map(i=>`<li>${i}</li>`).join('');
}

function renderFallback(symptoms){
  const mockData = {
    primary_disease:'Common Cold',
    confidence:55.0,
    risk_level:'Low',
    top_predictions:[['Common Cold',55.0],['Allergy',22.0],['Bronchial Asthma',12.0],['Fungal infection',7.0],['Drug Reaction',4.0]],
    symptoms_used: symptoms.slice(0,6)
  };
  renderResult(mockData);
  const note = document.createElement('div');
  note.style.cssText='font-size:.72rem;color:var(--text3);background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:8px;padding:8px 12px;margin-top:12px';
  note.textContent='Could not reach the API — showing demo result. The backend may be waking up (free tier). Try again in 30 seconds.';
  const card = document.getElementById('resCard');
  if(card) card.appendChild(note);
}

document.addEventListener('DOMContentLoaded', loadResult);
