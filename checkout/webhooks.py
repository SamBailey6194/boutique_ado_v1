import json
import stripe
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .webhook_handler import StripeWH_Handler


@require_POST
@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint.
    Verifies signature, parses the event, and dispatches to a handler class.
    """
    # Set Stripe secret key (used if you make API calls in handlers)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get raw body and signature header
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = settings.STRIPE_WH_SECRET

    try:
        # Verify event signature & construct event
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except ValueError:
        # Invalid payload (not valid JSON)
        return HttpResponseBadRequest("Invalid payload")
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponseBadRequest("Invalid signature")
    except Exception as e:
        return HttpResponse(status=400, content=str(e))

    # Create webhook handler instance
    handler = StripeWH_Handler(request)

    # Map event types to handler methods
    event_map = {
        "payment_intent.succeeded": handler.handle_payment_intent_succeeded,
        "payment_intent.payment_failed": handler.handle_payment_intent_failed,
    }

    # Get handler from map or use default
    event_type = event["type"]
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the handler
    response = event_handler(event)

    print('Success!')
    return response or HttpResponse(status=200)
