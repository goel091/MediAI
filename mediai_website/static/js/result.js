/* result.js — Result page: fetch prediction & display with precautions */
'use strict';

function fmt(s){ return (s||'').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase()); }

async function loadResult(){
  const symptoms = JSON.parse(sessionStorage.getItem('mediai_symptoms') || '[]');

  if(!symptoms.length){
    // No symptoms — redirect back
    document.getElementById('resLoading').innerHTML = `
      <div style="text-align:center;padding:40px">
        <p style="color:var(--text2);margin-bottom:16px">No symptoms found. Please go back and select symptoms.</p>
        <a class="btn-primary" href="/diagnose">← Go to Diagnosis</a>
      </div>`;
    return;
  }

  try{
    const res = await fetch('/api/predict',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({symptoms, top_k:5})
    });
    const data = await res.json();
    if(data.error) throw new Error(data.error);
    renderResult(data);
  } catch(e){
    renderFallback(symptoms);
  }
}

function renderResult(data){
  document.getElementById('resLoading').style.display = 'none';
  document.getElementById('resCard').style.display = 'block';
  document.getElementById('precPanel').style.display = 'block';

  // Risk badge
  const risk = (data.risk_level||'Low').toLowerCase();
  const riskEl = document.getElementById('resRisk');
  riskEl.textContent = (data.risk_level||'Low').toUpperCase() + ' RISK';
  riskEl.className = 'res-risk-badge ' + risk;

  // Disease name
  document.getElementById('resDisease').textContent = data.primary_disease;

  // Confidence
  const conf = parseFloat(data.confidence)||0;
  document.getElementById('resConf').textContent = conf.toFixed(1) + '%';
  setTimeout(()=>{ document.getElementById('resBar').style.width = conf + '%'; }, 80);

  // Top 5
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

  // Symptoms used
  const sc = document.getElementById('resSyms');
  sc.innerHTML = (data.symptoms_used||[]).map(s=>`<span class="res-sym-chip">${fmt(s)}</span>`).join('');

  // Precautions
  renderPrecautions(data.primary_disease);
}

function renderPrecautions(diseaseName){
  const prec = window.PRECAUTIONS[diseaseName];
  document.getElementById('precDisease').textContent = diseaseName;

  if(!prec){
    document.getElementById('precPanel').innerHTML = `
      <div class="prec-header">
        <svg viewBox="0 0 24 24" fill="none" width="18" height="18"><path d="M12 2L3 7v5c0 5.5 4 10.7 9 12 5-1.3 9-6.5 9-12V7L12 2z" stroke="currentColor" stroke-width="1.5"/></svg>
        Precautions for ${diseaseName}
      </div>
      <p style="font-size:.875rem;color:var(--text2);line-height:1.7;margin-top:12px">
        Please consult a qualified healthcare professional for specific precautions and treatment advice for <strong>${diseaseName}</strong>.
      </p>
      <div class="prec-note" style="margin-top:16px">Always seek professional medical advice before making any health decisions.</div>`;
    return;
  }

  document.getElementById('precDoList').innerHTML   = prec.do.map(i=>`<li>${i}</li>`).join('');
  document.getElementById('precAvoidList').innerHTML = prec.avoid.map(i=>`<li>${i}</li>`).join('');
  document.getElementById('precEmergList').innerHTML = prec.emergency.map(i=>`<li>${i}</li>`).join('');
}

function renderFallback(symptoms){
  // Demo result when API unavailable
  const mockDisease = 'Allergy';
  const mockData = {
    primary_disease: mockDisease,
    confidence: 52.5,
    risk_level: 'Medium',
    top_predictions: [[mockDisease,52.5],['Common Cold',22.0],['Fungal infection',12.3],['Drug Reaction',8.1],['Gastroenteritis',5.1]],
    symptoms_used: symptoms.slice(0,6)
  };
  renderResult(mockData);

  // Add demo note
  const note = document.createElement('div');
  note.style.cssText='font-size:.72rem;color:var(--text3);background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);border-radius:8px;padding:8px 12px;margin-top:12px';
  note.textContent='Demo mode — run python app.py for real ML predictions.';
  document.getElementById('resCard').appendChild(note);
}

document.addEventListener('DOMContentLoaded', loadResult);
