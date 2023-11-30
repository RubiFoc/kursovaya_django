from django.urls import reverse
from django.db import models

from user.models import User


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название мероприятия")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фото")
    time_start = models.DateTimeField(verbose_name="Время проведения")
    is_published = models.BooleanField(default=False, verbose_name="Публикация")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name="Категории")
    price = models.FloatField(default=0, verbose_name='Цена билета')
    count_tickets = models.PositiveIntegerField(default=0, verbose_name='Количество билетов')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятие'
        ordering = ['id']


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']


class Purchase(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Мероприятие")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Покупатель")
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата покупки")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество билетов")
    total_price = models.FloatField(verbose_name="Общая стоимость")

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'


class EventCreation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Мероприятие",
                              related_name='event_creations')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Создатель",
                                related_name='created_events')
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество билетов")
    price = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Стоимость билета",
                              related_name='event_prices')

    class Meta:
        verbose_name = 'Созданное организатором мероприятие'
        verbose_name_plural = 'Созданные организаторами мероприятия'