const enetete=document.getElementsByClassName("entete")[0];
const btn = document.getElementById('btn-menu');
const liens = document.getElementById('liens');

btn.addEventListener('click', () => {
  liens.classList.toggle('ouvert');
  btn.textContent = liens.classList.contains('ouvert') ? '✕' : '☰';
});