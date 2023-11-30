from django.urls import path, re_path

from events.views import EventCategory, LoginUser, logout_user, RegisterUser, EventHome, ShowPost, ProfileView, \
    UserProfileUpdateView, AddEvent, Search, PurchaseTicketView, OrganizerProfileView, EventEditView, CancelPurchaseView

urlpatterns = [
    path('', EventHome.as_view(), name='home'),
    path('category/<slug:cat_slug>/', EventCategory.as_view(), name='category'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('post/<slug:post_slug>/', ShowPost.as_view(), name='post'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('organizer_profile/<str:username>/', OrganizerProfileView.as_view(), name='organizer_profile'),
    path('profile/<str:username>/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('addevent/', AddEvent.as_view(), name='add_event'),
    path('search/', Search.as_view(), name='search'),
    path('purchase/<slug:slug>/', PurchaseTicketView.as_view(), name='purchase_ticket'),
    path('eventupdate/<slug:slug>/', EventEditView.as_view(), name='event_edit'),
    path('cancel_purchase/<int:pk>/', CancelPurchaseView.as_view(), name='cancel_purchase'),
]
