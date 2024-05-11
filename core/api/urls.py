from rest_framework.routers import DefaultRouter
from website.api.urls import web_router
from django.urls import path, include


router = DefaultRouter()

router.registry.extend(web_router.registry)

urlpatterns = [
    path('', include(router.urls))

]