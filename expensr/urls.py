from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from expenses.views import register, login, ExpenseViewSet, MonthlySummaryView

router = DefaultRouter()
router.register(r"expenses", ExpenseViewSet, basename="expense")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("", include(router.urls)),  # includes /expenses/ and /expenses/{id}/
    path("summary/monthly/", MonthlySummaryView.as_view(), name="monthly-summary"),
]
