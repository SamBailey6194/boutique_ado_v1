# profiles/forms.py
from django import forms
from allauth.account.forms import SignupForm
from .models import UserProfile, UserAddress
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


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'First Name'}
            )
        )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Last Name'}
            )
        )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}
            )
        )

    class Meta:
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'email',
            'default_phone_number',
            'default_country',
            'default_postcode',
            'default_town_or_city',
            'default_street_address1',
            'default_street_address2',
            'default_county',
        )
        widgets = {
            'default_country': CountrySelectWidget(),
        }

    # Optional: Add placeholders and CSS classes for better UI
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-populate the user fields
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

        placeholders = {
            'default_phone_number': 'Phone Number',
            'default_postcode': 'Postcode',
            'default_town_or_city': 'Town or City',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_county': 'County',
        }
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'label',
            'phone_number',
            'country',
            'postcode',
            'town_or_city',
            'street_address1',
            'street_address2',
            'county'
        ]
        widgets = {
            'country': CountrySelectWidget(
                attrs={'class': 'form-control stripe-style-input'}
                ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control stripe-style-input'
