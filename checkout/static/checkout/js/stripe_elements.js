document.addEventListener('DOMContentLoaded', function() {
    // Get keys from Django
    const stripe_public_key = JSON.parse(document.getElementById('id_stripe_public_key').textContent);
    const client_secret = JSON.parse(document.getElementById('id_client_secret').textContent);

    // Initialize Stripe (Basil)
    const stripe = Stripe(stripe_public_key);
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

    card.addEventListener('change', function(event) {
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
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const { error, paymentIntent } = await stripe.confirmCardPayment(client_secret, {
            payment_method: { card }
        });

        if (error) {
            document.getElementById('card-errors').textContent = error.message;
        } else if (paymentIntent.status === "succeeded") {
            alert("Payment successful!");
            // Optionally redirect or update your backend
        }
    });
});
