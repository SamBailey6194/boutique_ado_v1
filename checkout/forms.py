from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    save_this_address = forms.BooleanField(
        required=False,
        initial=False,
        label="Save this address to your profile"
    )

    class Meta:
        model = Order
        fields = (
            'full_name',
            'email',
            'phone_number',
            'country',
            'postcode',
            'town_or_city',
            'street_address1',
            'street_address2',
            'county',
        )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal or ZIP Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True

        for field_name, field in self.fields.items():
            # Use get() with default '' so KeyError doesn't happen
            base_placeholder = placeholders.get(field_name, '')
            if field_name != 'country' and field.required and base_placeholder:
                placeholder = f'{base_placeholder} *'
            else:
                placeholder = base_placeholder

            field.widget.attrs['placeholder'] = placeholder

            # Apply classes to all fields
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (
                f'{existing_classes} stripe-style-input'.strip()
                )
            field.label = False

        self.fields['country'].empty_label = 'Country *'
