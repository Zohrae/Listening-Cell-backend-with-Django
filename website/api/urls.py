from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import VisiteurViewSet, ÉtudiantViewSet,  AdministrateurViewSet, ConseillerViewSet, NotificationViewSet, DemandeViewSet, NotificationEtudiantViewSet

web_router = DefaultRouter()


web_router.register(r'visiteurs', VisiteurViewSet)
web_router.register(r'etudiants', ÉtudiantViewSet)
web_router.register(r'conseillers', ConseillerViewSet)
web_router.register(r'administrateurs', AdministrateurViewSet)
web_router.register(r'demandes', DemandeViewSet)
web_router.register(r'notifications', NotificationViewSet)
web_router.register(r'notificationsEtudiant', NotificationEtudiantViewSet)








