from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import time
import stripe
import json
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile, UserAddress


class StripeWH_Handler:
    """
    Handle Stripe Webhooks
    """
    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """
        Send the user a confirmstion email
        """
        cust_email = order.email
        order_detail_url = self.request.build_absolute_uri(
            reverse('checkout:order_detail', args=[order.order_number])
        )

        # Send confirmation email
        subject = f"Order Confirmation - {order.order_number}"
        message = render_to_string(
            'checkout/emails/order_confirmation_email.html',
            {'order': order, 'order_detail_url': order_detail_url}
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email],
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200,
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details  # updated
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)  # updated

        email = (getattr(shipping_details, 'email', None) or
                 intent.receipt_email or
                 billing_details.email
                 )
        phone = (getattr(shipping_details, 'phone', None) or
                 billing_details.phone
                 )

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        try:
            user_profile = UserProfile.objects.get(user__email=email)
        except UserProfile.DoesNotExist:
            user_profile = None

        # Update profile information if save_info was checked
        if user_profile and save_info == 'true':
            user_profile.default_phone_number = phone
            user_profile.default_country = shipping_details.address.country
            user_profile.default_postcode = (
                shipping_details.address.postal_code
                )
            user_profile.default_town_or_city = shipping_details.address.city
            user_profile.default_street_address1 = (
                shipping_details.address.line1
                )
            user_profile.default_street_address2 = (
                shipping_details.address.line2
                )
            user_profile.default_county = shipping_details.address.state
            user_profile.save()

            UserAddress.objects.get_or_create(
                user=user_profile.user,
                full_name=shipping_details.name,
                phone_number=phone,
                country=shipping_details.address.country,
                postcode=shipping_details.address.postal_code,
                town_or_city=shipping_details.address.city,
                street_address1=shipping_details.address.line1,
                street_address2=shipping_details.address.line2,
                county=shipping_details.address.state,
            )

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=email,
                    phone_number__iexact=phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event['type']} | '
                'SUCCESS: Verified order already in database',
                status=200,
            )
        else:
            order = None
            try:
                order = Order.objects.create(
                            user_profile=user_profile,
                            full_name=shipping_details.name,
                            email=email,
                            phone_number=phone,
                            country=shipping_details.address.country,
                            postcode=(
                                shipping_details.address.postal_code
                                ),
                            town_or_city=shipping_details.address.city,
                            street_address1=(
                                shipping_details.address.line1
                                ),
                            street_address2=(
                                shipping_details.address.line2
                                ),
                            county=shipping_details.address.state,
                            grand_total=grand_total,
                            original_bag=bag,
                            stripe_pid=pid,
                        )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        OrderLineItem.objects.create(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                    else:
                        for size, quantity in (
                            item_data['items_by_size'].items()
                        ):
                            OrderLineItem.objects.create(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(content='Webhook received:  '
                                    f'{event["type"]} | ERROR: {e}',
                                    status=500,
                                    )
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | '
            'SUCCESS: Created order in webhook',
            status=200,
        )

    def handle_payment_intent_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200,
        )
