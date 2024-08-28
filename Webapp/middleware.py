from django.utils.deprecation import MiddlewareMixin
from .models import userdatas, Mechanics


class CustomAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        mechanic_id = request.session.get('Mechid')
        user_id = request.session.get('Userid')

        if mechanic_id:
            try:
                request.mechanic = Mechanics.objects.get(pk=mechanic_id)
            except Mechanics.DoesNotExist:
                request.mechanic = None
        else:
            request.mechanic = None

        if user_id:
            try:
                request.userdata = userdatas.objects.get(pk=user_id)
            except user_id.DoesNotExist:
                request.userdata = None
        else:
            request.userdata = None
