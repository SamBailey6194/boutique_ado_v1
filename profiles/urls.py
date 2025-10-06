from django.urls import path
from . import views

app_name = 'profiles'


urlpatterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path(
        'address/add/',
        views.AddressCreateView.as_view(),
        name='add_address'
        ),
    path('address/<int:pk>/edit/',
         views.AddressUpdateView.as_view(),
         name='edit_address'
         ),
    path('address/<int:pk>/delete/',
         views.AddressDeleteView.as_view(),
         name='delete_address'
         ),
]
