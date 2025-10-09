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
    path(
        'cache_checkout_data/',
        views.cache_checkout_data,
        name='cache_checkout_data'
    ),
    path('webhook/', stripe_webhook, name='webhook'),
    path(
        'order/<str:order_number>/change-request/',
        views.submit_order_change_request,
        name='request_order_change'
    ),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
]
