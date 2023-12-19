from django.db.models import Count
from django.core.cache import cache
from .models import *


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        cats = cache.get('cats')
        if not cats:
            cats = Category.objects.annotate(Count('event'))
            cache.set('cats', cats, 60)

        context['cats'] = cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context
