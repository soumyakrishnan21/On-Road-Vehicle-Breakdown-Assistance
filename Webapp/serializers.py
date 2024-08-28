from Webapp.models import UserRequests
from rest_framework import serializers


class User_serailzers(serializers.ModelSerializer):
    class Meta:
        model = UserRequests
        fields = [
            'id', 'Mechid', 'Userid', 'latitude','longitude','status'
        ]



