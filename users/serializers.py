from rest_framework import serializers
from .models import User, ShippingAddress


class AccountProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for representing and validating a user's account profile data.

    This serializer is used to interact with user profile-related data. It ensures that the data
    is serialized and deserialized correctly when interacting with the User model, particularly
    with specified fields like `first_name`, `last_name`, `email`, `phone`, and `image`.

    Inherits from `serializers.ModelSerializer`, which provides an implementation for mapping
    model instances to JSON format and handling validation logic based on the Django model.

    :ivar Meta.model: The model associated with this serializer, which is the `User` model in
        this case.
    :type Meta.model: User
    :ivar Meta.fields: Fields of the `User` model serialized by this serializer, which include
        "first_name", "last_name", "email", "phone", and "image".
    :type Meta.fields: tuple
    """

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "image")


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        exclude = ("user",)
