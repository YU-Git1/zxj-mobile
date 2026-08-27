const billingButtons = document.querySelectorAll('.billing-option');
const priceElements = document.querySelectorAll('[data-monthly]');
billingButtons.forEach((button) => {
  button.addEventListener('click', () => {
    billingButtons.forEach((item) => item.classList.remove('selected'));
    button.classList.add('selected');
    const period = button.dataset.period;
    priceElements.forEach((price) => {
      price.textContent = price.dataset[period];
    });
  });
});

document.querySelectorAll('.faq-item').forEach((item) => {
  item.addEventListener('toggle', () => {
    const icon = item.querySelector('.chevron');
    if (icon) icon.textContent = item.open ? '⌃' : '⌄';
  });
});

const allLayer = document.querySelector('[data-layer="all"]');
const layerControls = document.querySelectorAll('.layer-menu input[data-layer]:not([data-layer="all"])');
const layerImage = document.getElementById('layerImage');
const revealStyle = document.createElement('style');
revealStyle.textContent = `.reveal-target{opacity:0;transform:translateY(16px);transition:opacity .6s ease,transform .6s ease;will-change:opacity,transform}.reveal-target.is-visible{opacity:1;transform:none}.reveal-target[data-reveal-delay="1"]{transition-delay:.08s}.reveal-target[data-reveal-delay="2"]{transition-delay:.16s}.reveal-target[data-reveal-delay="3"]{transition-delay:.24s}@media(prefers-reduced-motion:reduce){.reveal-target{opacity:1;transform:none;transition:none}}`;
document.head.appendChild(revealStyle);
if (allLayer && layerImage) {
  const syncLayers = () => {
    const active = [...layerControls].filter((input) => input.checked).length;
    layerImage.style.filter = active === 0 ? 'grayscale(1) brightness(.25)' : `saturate(${0.55 + active * 0.15}) brightness(${0.7 + active * 0.06})`;
    allLayer.checked = active === layerControls.length;
  };
  allLayer.addEventListener('change', () => { layerControls.forEach((input) => { input.checked = allLayer.checked; }); syncLayers(); });
  layerControls.forEach((input) => input.addEventListener('change', syncLayers));
  syncLayers();
}

const revealTargets = document.querySelectorAll('.section-heading, .copy, .glass-card, .generation-copy, .generation-grid > img, .steps > div, .platform-groups > div, .start .section-heading, .start .primary-button');
revealTargets.forEach((element, index) => {
  element.classList.add('reveal-target');
  if (element.matches('.glass-card, .steps > div')) element.dataset.revealDelay = String(index % 4);
});
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => { if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); } });
  }, { threshold: 0.12, rootMargin: '0px 0px -30px' });
  revealTargets.forEach((element) => revealObserver.observe(element));
} else revealTargets.forEach((element) => element.classList.add('is-visible'));
