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
