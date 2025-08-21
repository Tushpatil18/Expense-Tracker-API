from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Expense
from .serializers import RegisterSerializer, ExpenseSerializer


# ---- Auth ----
@api_view(["POST"])
def register(request):
    """
    POST /register {email, password, name}
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "User created"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    """
    POST /login {email, password} -> {access, refresh}
    """
    email = (request.data.get("email") or "").lower()
    password = request.data.get("password") or ""
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "Invalid credentials"}, status=400)
    if not user.check_password(password):
        return Response({"detail": "Invalid credentials"}, status=400)
    refresh = RefreshToken.for_user(user)
    return Response({"access": str(refresh.access_token), "refresh": str(refresh)})


# ---- Permissions ----
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# ---- Expenses CRUD ----
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    # Ordering allowed by 'date' and 'amount'
    ordering_fields = ["date", "amount"]

    def get_queryset(self):
        qs = Expense.objects.filter(user=self.request.user)
        q = self.request.query_params
        if q.get("startDate"):
            qs = qs.filter(date__gte=q.get("startDate"))
        if q.get("endDate"):
            qs = qs.filter(date__lte=q.get("endDate"))
        if q.get("category"):
            qs = qs.filter(category=q.get("category"))
        if q.get("minAmount"):
            qs = qs.filter(amount__gte=q.get("minAmount"))
        if q.get("maxAmount"):
            qs = qs.filter(amount__lte=q.get("maxAmount"))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---- Monthly Summary ----
class MonthlySummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rows = (
            Expense.objects.filter(user=request.user)
            .annotate(month=TruncMonth("date"))
            .values("month", "category")
            .annotate(total=Sum("amount"))
            .order_by("month", "category")
        )
        out = {}
        for r in rows:
            key = r["month"].strftime("%Y-%m")
            out.setdefault(key, {})
            out[key][r["category"]] = float(r["total"])
        return Response(out)
