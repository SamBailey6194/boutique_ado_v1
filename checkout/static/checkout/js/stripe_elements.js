document.addEventListener('DOMContentLoaded', () => {
    // Get keys from Django
    const stripePublicKey = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    const clientSecret = JSON.parse(document.getElementById('id_client_secret').textContent);

    // Initialize Stripe
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    // Card element style
    const style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': { color: '#aab7c4' }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };

    // Create and mount card Element
    const card = elements.create('card', { style });
    card.mount('#card-element');

    // Handle realtime validation errors
    card.addEventListener('change', (event) => {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.innerHTML = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            errorDiv.style.display = 'block';
        } else {
            errorDiv.textContent = '';
            errorDiv.style.display = 'none';
        }
    });

    // Handle form submission
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Disable inputs while processing
        card.update({ disabled: true });
        submitButton.disabled = true;

        const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: { card }
        });

        if (error) {
            // Show error and re-enable inputs
            const errorDiv = document.getElementById('card-errors');
            errorDiv.innerHTML = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${error.message}</span>
            `;
            errorDiv.style.display = 'block';
            card.update({ disabled: false });
            submitButton.disabled = false;
        } else if (paymentIntent.status === "succeeded") {
            // Submit to backend (Django view will finish the order)
            form.submit();
        }
    });
});
