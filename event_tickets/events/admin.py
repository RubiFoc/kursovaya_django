from django.contrib import admin
from django.utils.safestring import mark_safe

from events.models import Event, Category, Purchase, EventCreation
from user.models import User


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_start', 'get_html_photo', 'is_published', 'count_tickets', 'price')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'time_start')
    prepopulated_fields = {"slug": ("title",)}
    fields = (
        'title', 'slug', 'cat', 'content', 'photo', 'get_html_photo', 'count_tickets', 'price', 'is_published',
        'time_start')
    readonly_fields = ('get_html_photo',)
    save_on_top = True

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=50>")

    get_html_photo.short_description = "Миниатюра"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'avatar', 'date_joined', 'get_html_photo', 'is_organizer']

    def get_html_photo(self, object):
        if object.avatar:
            return mark_safe(f"<img src='{object.avatar.url}' width=50>")
        return mark_safe(
            "<img src='/static/events/images/avatar.png' width=50")  # Замените на свой путь к изображению по умолчанию

    get_html_photo.short_description = "Аватар"


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['event', 'buyer', 'purchase_date', 'quantity', 'total_price']


@admin.register(EventCreation)
class EventCreationAdmin(admin.ModelAdmin):
    list_display = ['event', 'creator', 'quantity', 'price']


admin.site.register(Event, EventAdmin)
admin.site.register(Category, CategoryAdmin)

admin.site.site_title = 'Админ-панель сайта по бронированию билетов на мероприятия и концерты'
admin.site.site_header = 'Админ-панель сайта по бронированию билетов на мероприятия и концерты'
