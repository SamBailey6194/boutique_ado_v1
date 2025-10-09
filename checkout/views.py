from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import stripe
import json
from .forms import OrderForm, OrderChangeRequestForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents
from profiles.models import UserAddress, UserProfile


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': (
                request.user.id
                if request.user.is_authenticated
                else 'anonymous'
                ),
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be '
                       'processed right now. Please try again later.'
                       )
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})

    # Redirect if bag is empty
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    # Use bag_contents to calculate totals
    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key

    # Create Stripe PaymentIntent (always create before rendering template)
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        capture_method='manual',
    )

    if request.method == 'POST':
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        order_form = OrderForm(form_data)

        if order_form.is_valid():
            # Save order
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)

            if request.user.is_authenticated:
                user_profile = get_object_or_404(
                    UserProfile, user=request.user
                    )
                order.user_profile = user_profile

            selected_address_id = request.POST.get('address_id')

            if selected_address_id == "" or selected_address_id == "default":
                # Use default profile address
                if request.user.is_authenticated:
                    profile = user_profile
                    order.phone_number = profile.default_phone_number
                    order.country = profile.default_country
                    order.postcode = profile.default_postcode
                    order.town_or_city = profile.default_town_or_city
                    order.street_address1 = profile.default_street_address1
                    order.street_address2 = profile.default_street_address2
                    order.county = profile.default_county
            else:
                # Use the selected saved address
                addr = get_object_or_404(
                    UserAddress, id=selected_address_id, user=request.user
                    )
                order.phone_number = addr.phone_number
                order.country = addr.country
                order.postcode = addr.postcode
                order.town_or_city = addr.town_or_city
                order.street_address1 = addr.street_address1
                order.street_address2 = addr.street_address2
                order.county = addr.county

            order.save()
            # Create OrderLineItems from bag
            for item_id, item_data in bag.items():
                try:
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
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our "
                        "database. Please call us for assistance!"
                    ))
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Save info for future reference if checkbox checked
            request.session['save_info'] = 'save-info' in request.POST

            # NEW: Update user profile if authenticated and checkbox checked
            if request.user.is_authenticated and request.session['save_info']:
                # Update single profile
                profile = user_profile
                profile.default_phone_number = order.phone_number
                profile.default_country = order.country
                profile.default_postcode = order.postcode
                profile.default_town_or_city = order.town_or_city
                profile.default_street_address1 = order.street_address1
                profile.default_street_address2 = order.street_address2
                profile.default_county = order.county
                profile.save()

                # Save to UserAddress if not already saved
                UserAddress.objects.get_or_create(
                    user=request.user,
                    phone_number=order.phone_number,
                    country=order.country,
                    postcode=order.postcode,
                    town_or_city=order.town_or_city,
                    street_address1=order.street_address1,
                    street_address2=order.street_address2,
                    county=order.county,
                )

            return redirect(
                reverse('checkout:checkout_success', args=[order.order_number])
                )
        else:
            messages.error(request, "There was an error with your form. "
                           "Please check your details.")
    else:
        if request.user.is_authenticated:
            saved_addresses = request.user.addresses.all()
            selected_address = None
            address_id = request.GET.get('address_id')
            if address_id:
                selected_address = (
                    saved_addresses.filter(id=address_id).first()
                    )

            # Pre-fill form from selected address, or default profile
            initial_data = {
                'full_name': (
                    selected_address.full_name
                    if selected_address
                    else
                    f'{request.user.first_name} '
                    f'{request.user.last_name}'
                    ),
                'email': request.user.email,
                'phone_number': (
                    selected_address.phone_number
                    if selected_address
                    else request.user.userprofile.default_phone_number
                    ),
                'country': (
                    selected_address.country
                    if selected_address
                    else request.user.userprofile.default_country
                    ),
                'postcode': (
                    selected_address.postcode
                    if selected_address
                    else request.user.userprofile.default_postcode
                    ),
                'town_or_city': (
                    selected_address.town_or_city
                    if selected_address
                    else request.user.userprofile.default_town_or_city
                    ),
                'street_address1': (
                    selected_address.street_address1
                    if selected_address
                    else request.user.userprofile.default_street_address1
                    ),
                'street_address2': (
                    selected_address.street_address2
                    if selected_address
                    else request.user.userprofile.default_street_address2
                    ),
                'county': (
                    selected_address.county
                    if selected_address
                    else request.user.userprofile.default_county
                    ),
            }

            order_form = OrderForm(initial=initial_data)
        else:
            order_form = OrderForm()

    # Show warning if Stripe public key missing
    if not stripe_public_key:
        messages.warning(
            request,
            'Stripe public key is missing. Did you forget to set it in your '
            'environment?'
        )

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
        'bag_items': current_bag['bag_items'],
        'total': current_bag['total'],
        'grand_total': current_bag['grand_total'],
        'delivery': current_bag['delivery'],
        'free_delivery_delta': current_bag['free_delivery_delta'],
        'free_delivery_threshold': current_bag['free_delivery_threshold'],
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle success checkouts
    """
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        order.user_profile = user_profile
        order.save()

        if save_info:
            user_profile.default_phone_number = order.phone_number
            user_profile.default_country = order.country
            user_profile.default_postcode = order.postcode
            user_profile.default_town_or_city = order.town_or_city
            user_profile.default_street_address1 = order.street_address1
            user_profile.default_street_address2 = order.street_address2
            user_profile.default_county = order.county
            user_profile.save()

            UserAddress.objects.create(
                user=request.user,
                full_name=order.full_name,
                phone_number=order.phone_number,
                country=order.country,
                postcode=order.postcode,
                town_or_city=order.town_or_city,
                street_address1=order.street_address1,
                street_address2=order.street_address2,
                county=order.county,
            )

    messages.success(request, f'Order successfully processed! '
                     f'Your order number is {order_number}. '
                     f'A confirmation email will be sent to {order.email}.'
                     )

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)


@login_required
@require_POST
def submit_order_change_request(request, order_number):
    """
    Handle submission of an order change request
    from a modal on the profile page.
    """
    order = get_object_or_404(Order, order_number=order_number)
    order_change_form = OrderChangeRequestForm(request.POST)

    if order_change_form.is_valid():
        change_request = order_change_form.save(commit=False)
        change_request.user = request.user
        change_request.order = order
        change_request.save()
        messages.success(request, "Your change request has been submitted.")
    else:
        messages.error(
            request, "There was an error submitting your change request."
            )

    return redirect('profiles:profile')


def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'checkout/order_detail.html', {'order': order})
