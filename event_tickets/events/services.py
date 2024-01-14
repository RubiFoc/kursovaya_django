from django.contrib import messages
from django.http import request
from django.shortcuts import render, redirect

from events.models import Event, Category, Purchase


class EventService:
    def get_all_events(self):
        return Event.objects.filter(is_published=True).select_related('cat').order_by('time_start')

    def get_category_events(self, cat_slug):
        return Event.objects.filter(cat__slug=cat_slug, is_published=True).select_related(
            'cat').order_by('time_start')

    def get_category(self, cat_slug):
        return Category.objects.get(slug=cat_slug)

    def get_searching_result(self, search_query):
        return Event.objects.filter(title__icontains=search_query, is_published=True)


class PurchaseService:
    def get_purchase_event(self, slug):
        return Event.objects.get(slug=slug)

    def make_purchase(self, quantity, event, user):
        total_price = quantity * event.price

        purchase = Purchase(event=event, buyer=user, quantity=quantity, total_price=total_price)
        purchase.save()

        event.count_tickets -= quantity
        event.save()

    def cancel_purchase(self, purchase):
        event = purchase.event
        quantity_to_return = purchase.quantity

        event.count_tickets += quantity_to_return
        event.save()

        purchase.delete()
