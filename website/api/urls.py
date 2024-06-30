from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *
web_router = DefaultRouter()



web_router.register(r'visiteurs', VisiteurViewSet)
web_router.register(r'etudiants', ÉtudiantViewSet)
web_router.register(r'conseillers', ConseillerViewSet)
web_router.register(r'administrateurs', AdministrateurViewSet)
web_router.register(r'demandes', DemandeViewSet)
web_router.register(r'notifications', NotificationViewSet)
web_router.register(r'notificationsEtudiant', NotificationEtudiantViewSet)
web_router.register(r'feedbacks', FeedbackViewSet)
web_router.register(r'events', EventViewSet)
web_router.register(r'dispos', DisponibiliteConseillerViewSet)
web_router.register(r'dossiers', DossierViewSet)
web_router.register(r'messages', MessageViewSet)
web_router.register(r'alerts', AlertViewSet)
web_router.register(r'questions', QuestionViewSet)
web_router.register(r'quotes', QuoteViewSet)
web_router.register(r'todos', TODOViewSet)
web_router.register(r'collaborateurs', CollaborateurViewSet)
web_router.register(r'observations', ObservationViewSet)
web_router.register(r'ressources', RessourceViewSet)










