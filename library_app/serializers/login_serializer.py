from rest_framework import serializers
from ..model.users import User

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]
