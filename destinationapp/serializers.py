from rest_framework import serializers
from .models import CustomUser, Country, State, District, Destination
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import CustomUser, Country, State, District
from django.contrib.auth import authenticate

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'country']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name', 'state']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'username', 'password', 'confirm_password', 'country', 'state', 'district']

    def create(self, validated_data):
        # Remove 'confirm_password' from validated_data
        validated_data.pop('confirm_password')

        # Hash the password
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)

        # Create and return the CustomUser instance
        user = CustomUser(**validated_data)
        user.save()  # Save the instance to the database
        return user  # Return the created user instance

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

        return {
            'id': user.id,
            'username' : username,
            'password': password
        }

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ['id', 'place_name', 'weather', 'state', 'district', 'google_map_link', 'Destination_img', 'description', 'created_by']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().update(instance, validated_data)
