# profiles/forms.py
from django import forms
from allauth.account.forms import SignupForm
from .models import UserProfile
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30, required=True, label="First Name"
        )
    last_name = forms.CharField(
        max_length=30, required=True, label="Last Name"
        )
    default_phone_number = forms.CharField(
        max_length=20, required=True, label="Phone Number"
        )
    default_country = CountryField().formfield(
        widget=CountrySelectWidget(), required=True
        )
    default_postcode = forms.CharField(
        max_length=20, required=True, label="Postcode"
        )
    default_town_or_city = forms.CharField(
        max_length=40, required=True, label="Town/City"
        )
    default_street_address1 = forms.CharField(
        max_length=80, required=True, label="Street Address 1"
        )
    default_street_address2 = forms.CharField(
        max_length=80, required=False, label="Street Address 2"
        )
    default_county = forms.CharField(
        max_length=80, required=False, label="County"
        )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)

        # Save first/last name on the user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        # Save the profile info
        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                'default_phone_number': self.cleaned_data[
                    'default_phone_number'
                    ],
                'default_country': self.cleaned_data[
                    'default_country'
                    ],
                'default_postcode': self.cleaned_data[
                    'default_postcode'
                    ],
                'default_town_or_city': self.cleaned_data[
                    'default_town_or_city'
                    ],
                'default_street_address1': self.cleaned_data[
                    'default_street_address1'
                    ],
                'default_street_address2': self.cleaned_data[
                    'default_street_address2'
                    ],
                'default_county': self.cleaned_data[
                    'default_county'
                    ],
            }
        )

        return user
