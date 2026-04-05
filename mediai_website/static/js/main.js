/* ═══════════════════════════════════════════════════════
   MediAI — main.js
   Full client-side logic: symptom loading, prediction API,
   animations, nav, stats counter, etc.
═══════════════════════════════════════════════════════ */

'use strict';

// ── State ──────────────────────────────────────────────────────────────────────
const state = {
  allSymptoms: [],
  selectedSymptoms: new Set(),
  currentCategory: 'all',
  searchQuery: '',
  lastResult: null,
};

// ── Category keyword map ───────────────────────────────────────────────────────
const CAT_KEYWORDS = {
  fever:  ['fever','shivering','chills','sweating','temperature','typhoid'],
  pain:   ['pain','ache','cramps','headache','backache','chest','joint','knee','hip','neck','belly','abdominal','bruising'],
  skin:   ['itching','rash','eruption','nodal','skin','blister','pimple','peeling','scurring','silver','inflammatory','blackhead','sore','crust','ooze','dischromic','patches'],
  gastro: ['vomiting','nausea','diarrhoea','stomach','indigestion','acidity','constipation','appetite','hunger','bowel','anal','passage_of_gas','belly','ulcer','bleeding','distention','gastro','liver','hepatitis'],
  neuro:  ['dizziness','unsteadiness','balance','spinning','slurred','sensorium','paralysis','weakness_of_one','brain','concentration','visual','blurred','smell','depression','anxiety','mood','irritability','coma'],
  resp:   ['cough','breathless','phlegm','sputum','congestion','sinus','throat','runny','chest_pain','asthma','bronchial','pneumonia'],
};

// ── Utility ───────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
function scrollTo(selector) {
  const el = document.querySelector(selector);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
function fmtSymptom(s) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// ── Nav scroll effect ─────────────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 60);
});

// ── Hamburger ─────────────────────────────────────────────────────────────────
document.getElementById('hamburger').addEventListener('click', function() {
  document.getElementById('navLinks').classList.toggle('open');
});

// ── Animated stats counter ────────────────────────────────────────────────────
function animateCounters() {
  document.querySelectorAll('.stat-num[data-target]').forEach(el => {
    const target = parseInt(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    let current = 0;
    const step  = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current.toLocaleString() + suffix;
      if (current >= target) clearInterval(timer);
    }, 25);
  });
}

// ── Intersection observer for stats ──────────────────────────────────────────
const statsObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) { animateCounters(); statsObserver.disconnect(); }
  });
}, { threshold: 0.3 });
const statsEl = document.querySelector('.statsbar');
if (statsEl) statsObserver.observe(statsEl);

// ── Load symptoms from API ────────────────────────────────────────────────────
async function loadSymptoms() {
  try {
    const res = await fetch('/api/symptoms');
    if (!res.ok) throw new Error('API unavailable');
    const data = await res.json();
    state.allSymptoms = data.symptoms;
    renderSymptoms();
  } catch (e) {
    // Fallback: hardcoded symptom list so the UI still works
    state.allSymptoms = [
      'abdominal_pain','abnormal_menstruation','acidity','acute_liver_failure','altered_sensorium',
      'anxiety','back_pain','belly_pain','blackheads','bladder_discomfort','blister','blood_in_sputum',
      'bloody_stool','blurred_and_distorted_vision','breathlessness','brittle_nails','bruising',
      'burning_micturition','chest_pain','chills','cold_hands_and_feets','congestion','constipation',
      'continuous_feel_of_urine','continuous_sneezing','cough','cramps','dark_urine','dehydration',
      'depression','diarrhoea','dischromic_patches','dizziness','drying_and_tingling_lips',
      'enlarged_thyroid','excessive_hunger','extra_marital_contacts','family_history','fast_heart_rate',
      'fatigue','fluid_overload','foul_smell_of_urine','headache','high_fever','hip_joint_pain',
      'history_of_alcohol_consumption','increased_appetite','indigestion','irritability','itching',
      'joint_pain','knee_pain','lack_of_concentration','lethargy','loss_of_appetite','loss_of_balance',
      'loss_of_smell','malaise','mild_fever','mood_swings','movement_stiffness','mucoid_sputum',
      'muscle_pain','muscle_wasting','muscle_weakness','nausea','neck_pain','nodal_skin_eruptions',
      'obesity','pain_behind_the_eyes','pain_during_bowel_movements','pain_in_anal_region',
      'painful_walking','palpitations','passage_of_gases','patches_in_throat','phlegm','polyuria',
      'prominent_veins_on_calf','puffy_face_and_eyes','pus_filled_pimples','red_spots_over_body',
      'redness_of_eyes','restlessness','runny_nose','rusty_sputum','shivering','sinus_pressure',
      'skin_peeling','skin_rash','slurred_speech','spinning_movements','spotting_urination',
      'stiff_neck','stomach_pain','sunken_eyes','sweating','swelled_lymph_nodes','swelling_joints',
      'swelling_of_stomach','swollen_legs','throat_irritation','ulcers_on_tongue','vomiting',
      'watering_from_eyes','weakness_in_limbs','weight_gain','weight_loss','yellow_urine',
      'yellowing_of_eyes','yellowish_skin',
    ];
    renderSymptoms();
  }
}

// ── Render symptom chips ──────────────────────────────────────────────────────
function renderSymptoms() {
  const grid = $('symGrid');
  grid.innerHTML = '';
  state.allSymptoms.forEach(sym => {
    const chip = document.createElement('span');
    chip.className = 'sym-chip';
    chip.dataset.sym = sym;
    chip.textContent = fmtSymptom(sym);

    // Apply visibility
    if (!isVisible(sym)) chip.classList.add('hidden');
    if (state.selectedSymptoms.has(sym)) chip.classList.add('selected');

    chip.addEventListener('click', () => toggleSymptom(chip, sym));
    grid.appendChild(chip);
  });
}

// ── Visibility check (search + category) ─────────────────────────────────────
function isVisible(sym) {
  const q = state.searchQuery.toLowerCase();
  const matchSearch = !q || sym.includes(q) || fmtSymptom(sym).toLowerCase().includes(q);

  let matchCat = true;
  if (state.currentCategory !== 'all') {
    const keywords = CAT_KEYWORDS[state.currentCategory] || [];
    matchCat = keywords.some(kw => sym.includes(kw));
  }
  return matchSearch && matchCat;
}

// ── Filter functions ──────────────────────────────────────────────────────────
function filterSymptoms(q) {
  state.searchQuery = q;
  applyFilters();
}
function filterCat(btn, cat) {
  state.currentCategory = cat;
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}
function applyFilters() {
  document.querySelectorAll('.sym-chip').forEach(chip => {
    const sym = chip.dataset.sym;
    chip.classList.toggle('hidden', !isVisible(sym));
  });
}

// ── Toggle symptom selection ──────────────────────────────────────────────────
function toggleSymptom(chip, sym) {
  if (state.selectedSymptoms.has(sym)) {
    state.selectedSymptoms.delete(sym);
    chip.classList.remove('selected');
  } else {
    state.selectedSymptoms.add(sym);
    chip.classList.add('selected');
  }
  updateSelectionUI();
}
function updateSelectionUI() {
  const n = state.selectedSymptoms.size;
  $('selCount').textContent = `${n} selected`;
  $('predictBtn').disabled = n < 1;
}
function clearAll() {
  state.selectedSymptoms.clear();
  document.querySelectorAll('.sym-chip').forEach(c => c.classList.remove('selected'));
  updateSelectionUI();
  showEmpty();
}

// ── Result panel states ───────────────────────────────────────────────────────
function showEmpty() {
  $('resultEmpty').style.display  = 'flex';
  $('resultLoading').style.display = 'none';
  $('resultCard').style.display    = 'none';
  $('resultPanel').style.alignItems = 'center';
}
function showLoading() {
  $('resultEmpty').style.display  = 'none';
  $('resultLoading').style.display = 'flex';
  $('resultCard').style.display    = 'none';
  $('resultPanel').style.alignItems = 'center';
}
function showResult() {
  $('resultEmpty').style.display  = 'none';
  $('resultLoading').style.display = 'none';
  $('resultCard').style.display    = 'block';
  $('resultPanel').style.alignItems = 'flex-start';
}

// ── PREDICTION ────────────────────────────────────────────────────────────────
async function predict() {
  const symptoms = [...state.selectedSymptoms];
  if (!symptoms.length) return;

  showLoading();

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symptoms, top_k: 5 }),
    });
    const data = await res.json();

    if (!res.ok || data.error) {
      throw new Error(data.error || 'Prediction failed');
    }

    renderResult(data);
  } catch (err) {
    // Graceful fallback with mock result when model not loaded
    renderFallbackResult(symptoms);
  }
}

// ── Render real ML result ─────────────────────────────────────────────────────
function renderResult(data) {
  state.lastResult = data;
  showResult();

  // Risk badge
  const riskEl = $('rcRisk');
  riskEl.textContent = data.risk_level.toUpperCase() + ' RISK';
  riskEl.className = 'rc-badge risk-' + data.risk_level.toLowerCase();

  // Disease
  $('rcDisease').textContent = data.primary_disease;

  // Confidence bar
  const conf = data.confidence;
  $('rcConf').textContent = conf.toFixed(1) + '%';
  setTimeout(() => { $('rcBar').style.width = conf + '%'; }, 50);

  // Top 5
  const top5 = $('rcTop5');
  top5.innerHTML = '';
  data.top_predictions.forEach((pred, i) => {
    const [disease, pct] = pred;
    top5.insertAdjacentHTML('beforeend', `
      <div class="rc-pred-item">
        <span class="rc-pred-name">${disease}</span>
        <div class="rc-pred-bar-outer">
          <div class="rc-pred-bar-inner ${i===0?'first':'other'}" style="width:0%" data-w="${pct}"></div>
        </div>
        <span class="rc-pred-pct">${pct.toFixed(1)}%</span>
      </div>
    `);
  });
  setTimeout(() => {
    document.querySelectorAll('.rc-pred-bar-inner[data-w]').forEach(el => {
      el.style.width = el.dataset.w + '%';
    });
  }, 80);

  // Symptoms used
  const symsDiv = $('rcSymsUsed');
  symsDiv.innerHTML = (data.symptoms_used || []).map(s =>
    `<span class="rc-sym-chip">${fmtSymptom(s)}</span>`
  ).join('');
}

// ── Fallback result (when Flask API not running — static demo) ────────────────
const MOCK_DB = {
  itching:        { d:'Fungal infection',     conf:76 },
  skin_rash:      { d:'Allergy',              conf:68 },
  high_fever:     { d:'Malaria',              conf:82 },
  vomiting:       { d:'Gastroenteritis',      conf:71 },
  headache:       { d:'Migraine',             conf:65 },
  chest_pain:     { d:'Heart attack',         conf:80 },
  cough:          { d:'Common Cold',          conf:60 },
  breathlessness: { d:'Bronchial Asthma',     conf:74 },
  fatigue:        { d:'Tuberculosis',         conf:55 },
  joint_pain:     { d:'Arthritis',            conf:69 },
  dizziness:      { d:'Vertigo (Paroxysmal Positional Vertigo)', conf:72 },
  yellowish_skin: { d:'Hepatitis A',          conf:85 },
  weight_loss:    { d:'Diabetes',             conf:63 },
  nausea:         { d:'Typhoid',              conf:67 },
};
function renderFallbackResult(symptoms) {
  // Find best matching mock
  let best = null, bestConf = 0;
  symptoms.forEach(s => {
    if (MOCK_DB[s] && MOCK_DB[s].conf > bestConf) {
      best = MOCK_DB[s]; bestConf = MOCK_DB[s].conf;
    }
  });
  if (!best) best = { d: 'Allergy', conf: 45 };

  const risk = best.conf >= 75 ? 'High' : best.conf >= 55 ? 'Medium' : 'Low';

  // Build mock top5
  const mockTop = [
    [best.d, best.conf],
    ['Allergy', Math.max(5, best.conf - 25)],
    ['Common Cold', Math.max(3, best.conf - 35)],
    ['Viral infection', Math.max(2, best.conf - 42)],
    ['Drug Reaction', Math.max(1, best.conf - 50)],
  ];

  renderResult({
    primary_disease: best.d,
    confidence: best.conf,
    risk_level: risk,
    top_predictions: mockTop,
    symptoms_used: symptoms.slice(0, 8),
  });

  // Note that this is demo mode
  const note = document.createElement('div');
  note.style.cssText = 'font-size:0.75rem;color:#94A3B8;background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);border-radius:8px;padding:8px 12px;margin-top:12px;';
  note.textContent = 'Demo mode — run `python app.py` for real ML predictions.';
  $('resultCard').appendChild(note);
}

// ── Load diseases into grid ───────────────────────────────────────────────────
async function loadDiseases() {
  const DISEASES = [
    'AIDS','Acne','Alcoholic hepatitis','Allergy','Arthritis','Bronchial Asthma',
    'Cervical spondylosis','Chicken pox','Chronic cholestasis','Common Cold',
    'Dengue','Diabetes','Dimorphic hemorrhoids (piles)','Drug Reaction',
    'Fungal infection','GERD','Gastroenteritis','Heart attack','Hepatitis A',
    'Hepatitis B','Hepatitis C','Hepatitis D','Hepatitis E','Hypertension',
    'Hyperthyroidism','Hypoglycemia','Hypothyroidism','Impetigo','Jaundice',
    'Malaria','Migraine','Osteoarthritis','Paralysis (brain hemorrhage)',
    'Peptic ulcer disease','Pneumonia','Psoriasis','Tuberculosis','Typhoid',
    'Urinary tract infection','Varicose veins','Vertigo (Paroxysmal Positional Vertigo)',
  ];

  const grid = $('diseaseGrid');
  if (!grid) return;
  DISEASES.forEach(d => {
    const tag = document.createElement('span');
    tag.className = 'disease-tag';
    tag.textContent = d;
    tag.title = `Click to diagnose ${d}`;
    grid.appendChild(tag);
  });
}

// ── Share result ───────────────────────────────────────────────────────────────
function shareResult() {
  if (!state.lastResult) return;
  const text = `MediAI Diagnosis: ${state.lastResult.primary_disease} (${state.lastResult.confidence.toFixed(1)}% confidence)\nSymptoms: ${state.lastResult.symptoms_used.join(', ')}\n\n⚠ Educational use only. Always consult a doctor.`;
  if (navigator.share) {
    navigator.share({ title: 'MediAI Result', text }).catch(() => {});
  } else {
    navigator.clipboard.writeText(text).then(() => {
      alert('Result copied to clipboard!');
    }).catch(() => {
      alert(text);
    });
  }
}

// ── Scroll-triggered fade-in ──────────────────────────────────────────────────
const fadeObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.how-card, .perf-card, .about-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  fadeObserver.observe(el);
});

// ── Init ───────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadSymptoms();
  loadDiseases();
  showEmpty();
});
