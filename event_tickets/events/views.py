from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from user.forms import UserProfileForm, RegisterUserForm, LoginUserForm
from user.models import User
from .forms import AddEventForm, PurchaseForm
from .models import Event, Category, Purchase, EventCreation
from .utils import DataMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


class EventHome(DataMixin, ListView):
    model = Event
    template_name = 'events/posts.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная страница")

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Event.objects.filter(is_published=True).select_related('cat')


class EventCategory(DataMixin, ListView):
    model = Event
    template_name = 'events/posts.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Event.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                      cat_selected=context['posts'][0].cat.pk)

        return dict(list(context.items()) + list(c_def.items()))


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


def logout_user(request):
    logout(request)
    return redirect('login')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


class ShowPost(DataMixin, DetailView):
    model = Event
    template_name = 'events/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'
    permission_classes = (IsAuthenticated,)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        return dict(list(context.items()) + list(c_def.items()))


class ProfileView(DetailView):
    template_name = 'events/profile.html'
    model = User
    context_object_name = 'user'
    blocks_per_page = 2  # Количество покупок на странице
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user  # Отображаем профиль текущего пользователя

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        purchases = Purchase.objects.filter(buyer=user).order_by('-purchase_date')

        paginator = Paginator(purchases, self.blocks_per_page)
        page = self.request.GET.get('page')
        purchases = paginator.get_page(page)

        context['purchases'] = purchases
        return context


class OrganizerProfileView(ProfileView):
    template_name = 'events/organizer_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Добавляем информацию об организаторе
        if self.request.user.is_organizer:
            events_created = EventCreation.objects.filter(creator=self.request.user)
            context['events_created'] = events_created

            paginator1 = Paginator(events_created, self.blocks_per_page)
            page = self.request.GET.get('page')
            events_created = paginator1.get_page(page)

            context['events_created'] = events_created

        return context


class UserProfileUpdateView(UpdateView):

    model = User
    form_class = UserProfileForm
    template_name = 'events/profile_update.html'  # Create a template for the profile update form
    success_url = reverse_lazy('home')  # Define the URL to redirect to upon successful update

    def get_object(self, queryset=None):
        return self.request.user


class EventEditView(UpdateView):
    model = Event
    form_class = AddEventForm
    template_name = 'events/event_edit.html'
    success_url = reverse_lazy('home')


class AddEvent(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddEventForm
    template_name = 'events/addevent.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True
    permission_classes = (IsAuthenticated,)

    def form_valid(self, form):
        # Сначала создайте мероприятие
        event = form.save(commit=False)
        event.save()

        # Затем создайте запись в EventCreation
        event_creation = EventCreation(event=event, creator=self.request.user, quantity=event.count_tickets,
                                       price=event)
        event_creation.save()

        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Добавление мероприятия")
        return dict(list(context.items()) + list(c_def.items()))


class Search(DataMixin, ListView):
    template_name = 'events/posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Event.objects.filter(title__icontains=self.request.GET.get('search'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        c_def = self.get_user_context(title="Главная страница")
        return dict(list(context.items()) + list(c_def.items()))


class PurchaseTicketView(View):
    template_name = 'events/purchase_form.html'

    def get(self, request, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Event.DoesNotExist:
            return redirect('home')  # Перенаправляем на другую страницу, если мероприятие не найдено

        form = PurchaseForm(initial={'event': event})
        return render(request, self.template_name, {'form': form, 'event': event})

    def post(self, request, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Event.DoesNotExist:
            return redirect('home')

        form = PurchaseForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > event.count_tickets:
                # Handle insufficient ticket availability
                return render(request, 'purchase_failure.html')

            total_price = quantity * event.price

            # Create a Purchase instance
            purchase = Purchase(event=event, buyer=request.user, quantity=quantity, total_price=total_price)
            purchase.save()

            # Update the event's ticket count
            event.count_tickets -= quantity
            event.save()

            # Redirect to a success page
            return redirect('home')  # Замените 'events_posts' на имя URL для страницы успеха

        return render(request, self.template_name, {'form': form, 'event': event})


class CancelPurchaseView(View):
    def get(self, request, pk):
        username = self.request.user.username
        purchase = get_object_or_404(Purchase, pk=pk)

        # Убедимся, что пользователь, делающий запрос, является покупателем
        if request.user != purchase.buyer:
            messages.error(request, "У вас нет разрешения на отмену этой покупки.")
            return redirect('profile', username)  # Перенаправить на домашнюю страницу или другой подходящий URL

        event = purchase.event
        quantity_to_return = purchase.quantity

        # Обновим количество билетов для мероприятия
        event.count_tickets += quantity_to_return
        event.save()

        # Удалим запись о покупке
        purchase.delete()

        messages.success(request, "Покупка успешно отменена.")
        return redirect('profile', username)
