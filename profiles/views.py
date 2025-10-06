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


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        context['profile'] = user_profile
        context['form'] = UserProfileForm(instance=user_profile)
        context['addresses'] = self.request.user.addresses.all()

        # Add forms for modals
        context['add_address_form'] = UserAddressForm()
        context['edit_address_form'] = UserAddressForm()
        context['delete_address_form'] = UserAddressForm()

        return context

    def post(self, request, *args, **kwargs):
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


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = UserAddress

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, "Address deleted.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('profiles:profile')
