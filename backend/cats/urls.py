from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewset
router = DefaultRouter()
router.register(r"cats", views.CatViewSet, basename="cats")

app_name = "cats"

urlpatterns = [
    # API endpoints
    path("api/", include(router.urls)),
]
