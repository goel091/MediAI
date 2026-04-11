/* diseases.js — Disease directory page */
'use strict';

function renderDirectory(){
  const grid = document.getElementById('dirGrid');
  const names = Object.keys(window.PRECAUTIONS).sort();

  names.forEach(name=>{
    const prec = window.PRECAUTIONS[name];
    const symsPreview = prec.symptoms.slice(0,4).map(s=>s.replace(/_/g,' ')).join(', ');

    const card = document.createElement('div');
    card.className = 'dir-card';
    card.dataset.name = name.toLowerCase();
    card.innerHTML = `
      <div class="dir-card-name">${name}</div>
      <div class="dir-card-syms">${symsPreview}</div>
      <div class="dir-card-foot">
        <span class="dir-card-prec">${prec.do.length} precautions</span>
        <span class="dir-card-arrow">View →</span>
      </div>`;
    card.addEventListener('click',()=>openModal(name));
    grid.appendChild(card);
  });
}

function filterDir(q){
  const query = q.toLowerCase();
  document.querySelectorAll('.dir-card').forEach(card=>{
    card.classList.toggle('hidden', !card.dataset.name.includes(query));
  });
}

function openModal(name){
  const prec = window.PRECAUTIONS[name];
  if(!prec) return;

  document.getElementById('modalName').textContent = name;

  // Symptoms
  const symsEl = document.getElementById('modalSyms');
  symsEl.innerHTML = prec.symptoms.map(s=>`<span class="modal-sym-tag">${s.replace(/_/g,' ')}</span>`).join('');

  // Description
  document.getElementById('modalDesc').textContent = prec.desc;

  // Precautions
  document.getElementById('modalDo').innerHTML    = prec.do.map(i=>`<li>${i}</li>`).join('');
  document.getElementById('modalAvoid').innerHTML = prec.avoid.map(i=>`<li>${i}</li>`).join('');
  document.getElementById('modalEmerg').innerHTML = prec.emergency.map(i=>`<li>${i}</li>`).join('');

  document.getElementById('modalOverlay').style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeModal(){
  document.getElementById('modalOverlay').style.display = 'none';
  document.body.style.overflow = '';
}

// Close on Escape key
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeModal(); });

document.addEventListener('DOMContentLoaded', renderDirectory);
