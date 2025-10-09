from django.contrib import admin, messages
import stripe
from django.conf import settings
from .models import Order, OrderLineItem, OrderChangeRequest

stripe.api_key = settings.STRIPE_SECRET_KEY


# -------------------- OrderLineItem Inline -------------------- #
class OrderLineItemAdminInLine(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)


# -------------------- Admin Actions -------------------- #
@admin.action(
        description='Mark selected orders as accepted and capture payment'
        )
def make_accepted(modeladmin, request, queryset):
    for order in queryset:
        if order.status != 'accepted':
            try:
                stripe.PaymentIntent.capture(order.stripe_pid)
                order.status = 'accepted'
                order.save()
                modeladmin.message_user(
                    request,
                    f"Order {order.order_number} accepted and payment "
                    "captured."
                )
            except Exception as e:
                modeladmin.message_user(
                    request,
                    f"Failed to capture payment for {order.order_number}: {e}",
                    level=messages.ERROR
                )


@admin.action(
        description='Mark selected orders as declined and cancel payment'
        )
def make_declined(modeladmin, request, queryset):
    for order in queryset:
        if order.status != 'declined':
            try:
                stripe.PaymentIntent.cancel(order.stripe_pid)
                order.status = 'declined'
                order.save()
                modeladmin.message_user(
                    request,
                    f"Order {order.order_number} declined and payment "
                    "cancelled."
                )
            except Exception as e:
                modeladmin.message_user(
                    request,
                    f"Failed to cancel payment for {order.order_number}: {e}",
                    level=messages.ERROR
                )


# -------------------- Order Admin -------------------- #
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInLine,)

    readonly_fields = (
        'order_number',
        'date',
        'delivery_cost',
        'order_total',
        'grand_total',
        'original_bag',
        'stripe_pid',
    )

    fields = (
        'order_number',
        'date',
        'full_name',
        'email',
        'phone_number',
        'country',
        'postcode',
        'town_or_city',
        'street_address1',
        'street_address2',
        'county',
        'delivery_cost',
        'order_total',
        'grand_total',
        'original_bag',
        'stripe_pid',
        'status',
    )

    list_display = (
        'order_number',
        'date',
        'full_name',
        'grand_total',
        'status',
    )
    list_filter = ('status', 'date')
    search_fields = ('order_number', 'full_name', 'email')
    ordering = ('-date',)
    actions = [make_accepted, make_declined]


# -------------------- OrderChangeRequest Admin -------------------- #
@admin.register(OrderChangeRequest)
class OrderChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'reason', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'user__username')
    actions = [make_accepted, make_declined]
