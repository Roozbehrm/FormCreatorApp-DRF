from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "title", "parent", "color", "created_at")

    def validate_parent(self, value):
        request = self.context["request"]
        if value and value.owner_id != request.user.id:
            raise serializers.ValidationError("دسته‌ی والد باید متعلق به خودتان باشد.")
        return value

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
