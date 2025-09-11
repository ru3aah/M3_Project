from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer


class MyOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related("items__product")
        )
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")
