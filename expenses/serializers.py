from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Expense


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("email", "name", "password")

    def create(self, validated_data):
        email = validated_data["email"].lower()
        name = validated_data["name"]
        user = User(username=email, email=email)
        user.first_name = name
        user.set_password(validated_data["password"])
        user.save()
        return user


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "amount", "category", "description", "date", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_amount(self, v):
        if v <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return v

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)
