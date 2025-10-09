document.addEventListener("DOMContentLoaded", () => {
  const orderChangeModal = document.getElementById('orderChangeModal');

  orderChangeModal.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget; // Button that triggered modal
    const orderNumber = button.getAttribute('data-order-number');
    const form = orderChangeModal.querySelector('form');

    // Set correct form action URL
    form.action = `/checkout/order/${orderNumber}/change-request/`;
  });
});