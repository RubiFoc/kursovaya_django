from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .forms import AddEventForm, PurchaseForm
from .models import Event, Category, Purchase, EventCreation
from .utils import DataMixin
from rest_framework.permissions import IsAuthenticated


class EventHome(DataMixin, ListView):
    model = Event
    template_name = 'events/posts.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная страница")

        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Event.objects.filter(is_published=True).select_related('cat').order_by('time_start')


class EventCategory(DataMixin, ListView):
    model = Event
    template_name = 'events/posts.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Event.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related(
            'cat').order_by('time_start')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                      cat_selected=context['posts'][0].cat.pk)

        return dict(list(context.items()) + list(c_def.items()))


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
        event = form.save(commit=False)
        event.save()

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
        search_query = self.request.GET.get('search', '')
        return Event.objects.filter(title__icontains=search_query, is_published=True)

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
            return redirect('home')

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
                return render(request, 'events/purchase_failure.html')

            total_price = quantity * event.price

            purchase = Purchase(event=event, buyer=request.user, quantity=quantity, total_price=total_price)
            purchase.save()

            event.count_tickets -= quantity
            event.save()
            return redirect('home')

        return render(request, self.template_name, {'form': form, 'event': event})


class CancelPurchaseView(View):
    def get(self, request, pk):
        username = self.request.user.username
        purchase = get_object_or_404(Purchase, pk=pk)

        if request.user != purchase.buyer:
            messages.error(request, "У вас нет разрешения на отмену этой покупки.")
            return redirect('profile', username)

        event = purchase.event
        quantity_to_return = purchase.quantity

        event.count_tickets += quantity_to_return
        event.save()

        purchase.delete()

        messages.success(request, "Покупка успешно отменена.")
        return redirect('profile', username)
