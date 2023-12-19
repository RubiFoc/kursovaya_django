from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView, CreateView
from rest_framework.permissions import IsAuthenticated

from events.models import EventCreation, Purchase
from events.utils import DataMixin
from user.forms import UserProfileForm, LoginUserForm, RegisterUserForm
from user.models import User


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'events/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'events/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')


class ProfileView(DetailView):
    template_name = 'events/profile.html'
    model = User
    context_object_name = 'user'
    blocks_per_page = 2
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        purchases = Purchase.objects.filter(buyer=user).order_by('-purchase_date')

        paginator = Paginator(purchases, self.blocks_per_page)
        page = self.request.GET.get('page')
        purchases = paginator.get_page(page)

        context['purchases'] = purchases
        return context


class UserProfileUpdateView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'events/profile_update.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user


class OrganizerProfileView(ProfileView):
    template_name = 'events/organizer_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_organizer:
            events_created = EventCreation.objects.filter(creator=self.request.user).order_by('-pk')
            context['events_created'] = events_created

            paginator1 = Paginator(events_created, self.blocks_per_page)
            page = self.request.GET.get('page')
            events_created = paginator1.get_page(page)

            context['events_created'] = events_created

        return context


def logout_user(request):
    logout(request)
    return redirect('login')
