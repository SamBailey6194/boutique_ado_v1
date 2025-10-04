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
    const loadingOverlay = document.getElementById('loading-overlay');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Disable inputs while processing
        card.update({ disabled: true });
        submitButton.disabled = true;

        // Hide the form and show overlay
        form.classList.add("hidden");
        loadingOverlay.classList.add("active");

        // Get the save-info checkbox value
        const saveInfo = document.getElementById('id-save-info').checked;

        // Get the CSRF token from the hidden input
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        // Prepare the POST data
        const postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };

        // URL for the request
        const url = '/checkout/cache_checkout_data/';

        try {
            // Send POST to cache checkout data
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(postData),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const { error, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: { 
                    card,
                    billing_details: {
                        name: form.full_name.value.trim(),
                        phone: form.phone_number.value.trim(),
                        email: form.email.value.trim(),
                        address: {
                            line1: form.street_address1.value.trim(),
                            line2: form.street_address2.value.trim(),
                            city: form.town_or_city.value.trim(),
                            country: form.country.value.trim(),
                            state: form.county.value.trim(),
                        }
                    }
                },
                shipping: {
                    name: form.full_name.value.trim(),
                    phone: form.phone_number.value.trim(),
                    address: {
                        line1: form.street_address1.value.trim(),
                        line2: form.street_address2.value.trim(),
                        city: form.town_or_city.value.trim(),
                        country: form.country.value.trim(),
                        postal_code: form.postcode.value.trim(),
                        state: form.county.value.trim(),
                    }   
                }
            });

            if (error) {
                // Show error and re-enable inputs
                const errorDiv = document.getElementById('card-errors');
                errorDiv.innerHTML = `
                    <span class="icon" role="alert"><i class="fas fa-times"></i></span>
                    <span>${error.message}</span>
                `;
                errorDiv.style.display = 'block';

                // Revert UI
                form.classList.remove("hidden");
                loadingOverlay.classList.remove("active");
                card.update({ disabled: false });
                submitButton.disabled = false;
            } else if (paymentIntent.status === "succeeded") {
                // Submit to backend (Django view will finish the order)
                form.submit();
            }
        } catch (err) {
                // Equivalent to .fail() in jQuery
                console.error(err);
                location.reload(); // reload the page if caching fails
        }
    });
});
