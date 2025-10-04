from django.urls import path
from . import views
from .webhooks import stripe_webhook


app_name = 'checkout'


urlpatterns = [
    path('', views.checkout, name='checkout'),
    path(
        'checkout_success/<order_number>',
        views.checkout_success,
        name='checkout_success'
    ),
    path('wh/', stripe_webhook, name='webhook'),
]
