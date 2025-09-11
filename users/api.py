from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ShippingAddress
from .serializers import AccountProfileSerializer, ShippingAddressSerializer


class AccountProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # GET /api/account/profile/
        s = AccountProfileSerializer(request.user)
        return Response(s.data)

    @action(detail=False, methods=["patch", "put", "post"], url_path="update")
    def update_profile(self, request):
        s = AccountProfileSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)


class ShippingAddressViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data.get("is_default"):
            ShippingAddress.objects.filter(
                user=self.request.user, is_default=True
            ).update(is_default=False)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get("is_default"):
            ShippingAddress.objects.filter(
                user=self.request.user, is_default=True
            ).exclude(pk=self.get_object().pk).update(is_default=False)
        serializer.save()
