from events.models import Purchase, EventCreation


class UserProfileService:
    def get_purchases(self, user):
        return Purchase.objects.filter(buyer=user).order_by('-purchase_date')

    def get_created_event(self, user):
        return EventCreation.objects.filter(creator=user).order_by('-pk')
