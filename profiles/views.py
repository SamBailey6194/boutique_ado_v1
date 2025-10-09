# profiles/views.py
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DeleteView
    )
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import UserProfile, UserAddress
from .forms import UserProfileForm, UserAddressForm
from checkout.forms import OrderChangeRequestForm


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        context['profile'] = user_profile
        context['form'] = UserProfileForm(instance=user_profile)
        addresses = self.request.user.addresses.all()

        # Ensure at least one address exists
        if not addresses.exists():
            UserAddress.objects.create(
                user=self.request.user,
                full_name=(
                    f"{self.request.user.first_name} "
                    f"{self.request.user.last_name}"
                    ),
                phone_number=user_profile.default_phone_number,
                country=user_profile.default_country,
                postcode=user_profile.default_postcode,
                town_or_city=user_profile.default_town_or_city,
                street_address1=user_profile.default_street_address1,
                street_address2=user_profile.default_street_address2,
                county=user_profile.default_county,
                default=True
            )
            addresses = self.request.user.addresses.all()

        initial_data = {
            'full_name': (
                f"{self.request.user.first_name} "
                f"{self.request.user.last_name}"
                ),
            'phone_number': user_profile.default_phone_number,
        }

        context['addresses'] = addresses

        # Add forms for modals
        context['add_address_form'] = UserAddressForm(initial=initial_data)
        context['edit_address_form'] = UserAddressForm()
        context['delete_address_form'] = UserAddressForm()

        context['orders'] = user_profile.orders.all().order_by('-date')
        context['change_request_form'] = OrderChangeRequestForm()

        return context

    def post(self, request, *args, **kwargs):
        """
        Handle updating the profile info OR changing default address
        """
        # 1️⃣ Handle default address selection
        default_address_id = request.POST.get('default_address')
        if default_address_id:
            addresses = request.user.addresses.all()
            for addr in addresses:
                addr.default = str(addr.id) == default_address_id
                addr.save()
            messages.success(request, "Default address updated!")
            return redirect('profiles:profile')

        # 2️⃣ Handle profile form submission (optional, if you keep the form)
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated successfully.")
            return redirect('profiles:profile')

        messages.error(request, "Please correct the errors below.")
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = UserAddress
    form_class = UserAddressForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "New address added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profiles:profile')


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = UserAddress
    form_class = UserAddressForm

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Address updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profiles:profile')


# profiles/views.py
class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = UserAddress

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        user_addresses = request.user.addresses.all()

        if user_addresses.count() <= 1:
            messages.error(request, "You must have at least one address.")
            return redirect('profiles:profile')

        messages.info(request, "Address deleted.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profiles:profile')
