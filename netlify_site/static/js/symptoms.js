/* symptoms.js — Netlify version: API calls go to Render backend */
'use strict';

/* ── CHANGE THIS to your actual Render URL ─────────────────────────────────── */
const API_BASE = 'https://mediai-esbq.onrender.com';
/* ─────────────────────────────────────────────────────────────────────────── */

const CAT = {
  fever:  ['fever','shivering','chills','sweating','temperature'],
  pain:   ['pain','ache','cramp','headache','chest','joint','knee','hip','neck','belly','abdominal','bruising'],
  skin:   ['itching','rash','eruption','nodal','skin','blister','pimple','peeling','scurring','silver','inflammatory','blackhead','sore','crust','ooze','dischromic','patches'],
  gastro: ['vomiting','nausea','diarrhoea','stomach','indigestion','acidity','constipation','appetite','hunger','bowel','anal','belly','ulcer','bleeding','distention'],
  neuro:  ['dizziness','unsteadiness','balance','spinning','slurred','sensorium','weakness_of_one','concentration','visual','blurred','smell','depression','anxiety','mood','irritability','coma'],
  resp:   ['cough','breathless','phlegm','sputum','congestion','sinus','throat','runny','chest_pain'],
};

const FALLBACK_SYMPTOMS = ['abdominal_pain','acidity','anxiety','back_pain','blackheads','bladder_discomfort','blister','blood_in_sputum','bloody_stool','blurred_and_distorted_vision','breathlessness','brittle_nails','bruising','burning_micturition','chest_pain','chills','cold_hands_and_feets','congestion','constipation','continuous_feel_of_urine','continuous_sneezing','cough','cramps','dark_urine','dehydration','depression','diarrhoea','dizziness','enlarged_thyroid','excessive_hunger','fast_heart_rate','fatigue','foul_smell_of_urine','headache','high_fever','hip_joint_pain','increased_appetite','indigestion','irritability','itching','joint_pain','knee_pain','lack_of_concentration','lethargy','loss_of_appetite','loss_of_balance','loss_of_smell','malaise','mild_fever','mood_swings','movement_stiffness','mucoid_sputum','muscle_pain','muscle_wasting','muscle_weakness','nausea','neck_pain','nodal_skin_eruptions','obesity','pain_behind_the_eyes','pain_during_bowel_movements','pain_in_anal_region','painful_walking','palpitations','passage_of_gases','patches_in_throat','phlegm','polyuria','prominent_veins_on_calf','puffy_face_and_eyes','pus_filled_pimples','red_spots_over_body','redness_of_eyes','restlessness','runny_nose','rusty_sputum','shivering','sinus_pressure','skin_peeling','skin_rash','slurred_speech','spinning_movements','spotting_urination','stiff_neck','stomach_pain','sunken_eyes','sweating','swelled_lymph_nodes','swelling_joints','swelling_of_stomach','swollen_legs','throat_irritation','ulcers_on_tongue','vomiting','watering_from_eyes','weakness_in_limbs','weight_gain','weight_loss','yellow_urine','yellowing_of_eyes','yellowish_skin'];

let allSymptoms = [];
let selected    = new Set();
let currentCat  = 'all';
let searchQ     = '';

function fmt(s){ return s.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase()); }

async function checkModelStatus(){
  try{
    const r = await fetch(API_BASE + '/api/status');
    const d = await r.json();
    const banner = document.getElementById('modelBanner');
    if(!banner) return;
    if(d.ready){
      banner.style.display = 'none';
    } else if(d.error){
      banner.innerHTML = `<div class="model-banner error">⚠ Model error: ${d.error}</div>`;
    } else {
      banner.innerHTML = `<div class="model-banner loading"><div class="mini-spinner"></div><span>AI model is warming up — you can select symptoms now. Ready in ~30 seconds.</span></div>`;
      setTimeout(checkModelStatus, 5000);
    }
  } catch(e){
    const banner = document.getElementById('modelBanner');
    if(banner) banner.innerHTML = `<div class="model-banner error">⚠ Cannot reach API server. Using demo mode.</div>`;
  }
}

async function loadSymptoms(){
  try{
    const r = await fetch(API_BASE + '/api/symptoms');
    if(!r.ok){ allSymptoms = FALLBACK_SYMPTOMS; renderChips(); return; }
    const d = await r.json();
    allSymptoms = d.symptoms || FALLBACK_SYMPTOMS;
  } catch(e){
    allSymptoms = FALLBACK_SYMPTOMS;
  }
  renderChips();
}

function isVisible(sym){
  const matchSearch = !searchQ || sym.includes(searchQ) || fmt(sym).toLowerCase().includes(searchQ);
  let matchCat = true;
  if(currentCat !== 'all'){
    const kws = CAT[currentCat]||[];
    matchCat = kws.some(k=>sym.includes(k));
  }
  return matchSearch && matchCat;
}

function renderChips(){
  const grid = document.getElementById('symGrid');
  if(!grid) return;
  grid.innerHTML = '';
  allSymptoms.forEach(sym=>{
    const el = document.createElement('span');
    el.className = 'sym-chip' + (!isVisible(sym)?' hidden':'') + (selected.has(sym)?' selected':'');
    el.dataset.sym = sym;
    el.textContent = fmt(sym);
    el.addEventListener('click',()=>toggle(el,sym));
    grid.appendChild(el);
  });
}

function toggle(el,sym){
  if(selected.has(sym)){selected.delete(sym);el.classList.remove('selected');}
  else{selected.add(sym);el.classList.add('selected');}
  updateUI();
}

function updateUI(){
  const n = selected.size;
  const badge = document.getElementById('selBadge');
  const btn   = document.getElementById('diagnoseBtn');
  const empty = document.getElementById('selEmpty');
  const chips = document.getElementById('selChips');
  const tip   = document.getElementById('selTip');
  if(badge) badge.textContent = n + ' selected';
  if(btn)   btn.disabled = n < 1;
  if(n===0){
    if(empty) empty.style.display='block';
    if(chips) chips.innerHTML='';
    if(tip)   tip.style.display='none';
    return;
  }
  if(empty) empty.style.display='none';
  if(tip)   tip.style.display = n < 3 ? 'flex' : 'none';
  if(chips){
    chips.innerHTML = '';
    selected.forEach(sym=>{
      const c = document.createElement('div');
      c.className = 'sel-chip-item';
      c.innerHTML = `<span>${fmt(sym)}</span><button class="sel-chip-remove" onclick="removeChip('${sym}')">✕</button>`;
      chips.appendChild(c);
    });
  }
}

function removeChip(sym){
  selected.delete(sym);
  const chip = document.querySelector(`.sym-chip[data-sym="${sym}"]`);
  if(chip) chip.classList.remove('selected');
  updateUI();
}

function filterSyms(q){
  searchQ = q.toLowerCase();
  document.querySelectorAll('.sym-chip').forEach(el=>{
    el.classList.toggle('hidden',!isVisible(el.dataset.sym));
  });
}

function setCat(btn,cat){
  currentCat = cat;
  document.querySelectorAll('.cat').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.sym-chip').forEach(el=>{
    el.classList.toggle('hidden',!isVisible(el.dataset.sym));
  });
}

function clearAll(){
  selected.clear();
  document.querySelectorAll('.sym-chip').forEach(c=>c.classList.remove('selected'));
  updateUI();
}

function goPredict(){
  if(!selected.size) return;
  sessionStorage.setItem('mediai_symptoms', JSON.stringify([...selected]));
  window.location.href = '/result';
}

document.addEventListener('DOMContentLoaded',()=>{
  checkModelStatus();
  loadSymptoms();
});
