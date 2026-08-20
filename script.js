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
