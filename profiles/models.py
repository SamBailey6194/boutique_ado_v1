from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


# Create your models here.
class UserProfile(models.Model):
    """
    A user profile model for maintaining default delivery
    information and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(
        max_length=20, null=False, blank=False
        )
    default_country = CountryField(null=False, blank=False)
    default_postcode = models.CharField(max_length=20, null=True, blank=False)
    default_town_or_city = models.CharField(
        max_length=40, null=False, blank=False
        )
    default_street_address1 = models.CharField(
        max_length=80, null=False, blank=False
        )
    default_street_address2 = models.CharField(
        max_length=80, null=True, blank=True
        )
    default_county = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return self.user.username


class UserAddress(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
        )
    label = models.CharField(
        max_length=50,
        default='My Address',
        help_text="e.g. Home, Work, Parents' House"
    )
    phone_number = models.CharField(max_length=20)
    country = CountryField()
    postcode = models.CharField(max_length=20)
    town_or_city = models.CharField(max_length=40)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, blank=True)
    county = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.street_address1}, {self.town_or_city}, {self.country}"
