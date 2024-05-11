from rest_framework.viewsets import ModelViewSet
from rest_framework import status , generics
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth import login as django_login
import json
from django.http import JsonResponse, request
from django.contrib.auth.hashers import check_password


from ..models import Visiteur, Etudiant, Administrateur, Conseiller, Demande, Notification, NotificationEtudiant
from .serializers import VisiteurSerializer, ÉtudiantSerializer, AdministrateurSerializer, ConseillerSerializer, DemandeSerializer, NotificationSerializer, NotificationEtudiantSerializer



class VisiteurViewSet(ModelViewSet):
    queryset = Visiteur.objects.all()
    serializer_class = VisiteurSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ÉtudiantViewSet(ModelViewSet):
    queryset = Etudiant.objects.all()
    serializer_class = ÉtudiantSerializer

class ConseillerViewSet(ModelViewSet):
    queryset = Conseiller.objects.all()
    serializer_class = ConseillerSerializer

    
class AdministrateurViewSet(ModelViewSet):
    queryset = Administrateur.objects.all()
    serializer_class = AdministrateurSerializer


logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            username = request.POST.get('username')
            password = request.POST.get('password')

        if username is not None and password is not None:
            try:
                conseiller = Conseiller.objects.get(nomUtilisateur=username, motDePasse=password)
                request.session['username'] = username
                request.session['conseiller_id'] = conseiller.id

                return JsonResponse({'id': conseiller.id}, status=200)

            except Conseiller.DoesNotExist:
                return JsonResponse({'detail': 'Invalid username or password.'}, status=401)
        else:
            return JsonResponse({'detail': 'Invalid request data.'}, status=400)
    return render(request, 'login.html')


def success(request):
    return render(request, 'success.html')


@csrf_exempt
def login_etudiant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            username = request.POST.get('username')
            password = request.POST.get('password')

        if username is not None and password is not None:
            try:
                etudiant = Etudiant.objects.get(nomUtilisateur=username, motDePasse=password)
                request.session['username'] = username
                request.session['etudiant_id'] = etudiant.id

                return JsonResponse({'id': etudiant.id}, status=200)


            except Etudiant.DoesNotExist:
                return JsonResponse({'detail': 'Invalid username or password.'}, status=401)
        else:
            return JsonResponse({'detail': 'Invalid request data.'}, status=400)
    return render(request, 'loginEtudiant.html')
    
def successEtudiant(request):
    return render(request, 'sucessEtudiant.html')


class DemandeViewSet(ModelViewSet):
    queryset = Demande.objects.all()
    serializer_class = DemandeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            conseiller = serializer.validated_data['conseiller']
            Notification.objects.create(conseiller=conseiller, message="Nouvelle demande ajoutée")

            etudiant = serializer.validated_data['etudiant']
            NotificationEtudiant.objects.create(etudiant=etudiant, message=f"Votre demande '{serializer.validated_data['title']}' a été soumise avec succès.")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            
            etudiant = instance.etudiant
            if instance.etat == 'Acceptée':
                message = f"Votre demande '{instance.title}' a été acceptée."
            elif instance.etat == 'Refusée':
                message = f"Votre demande '{instance.title}' a été refusée."
            else:
                message = f"Votre demande '{instance.title}' a été mise à jour."
            
            NotificationEtudiant.objects.filter(etudiant=etudiant, message=f"Votre demande '{instance.title}' a été soumise avec succès.").update(message=message)
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        conseiller_id = request.query_params.get('conseiller')

        if conseiller_id:
            demandes = self.queryset.filter(conseiller_id=conseiller_id)
            serializer = self.get_serializer(demandes, many=True)
            return Response(serializer.data)
        else:
            return super().list(request)


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def list(self, request):
        conseiller_id = request.query_params.get('conseiller')

        if conseiller_id:
            notifications = self.queryset.filter(conseiller_id=conseiller_id)
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        else:
            return super().list(request)


class NotificationEtudiantViewSet(ModelViewSet):
    queryset = NotificationEtudiant.objects.all()
    serializer_class = NotificationEtudiantSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        etudiant_id = request.query_params.get('etudiant')

        if etudiant_id:
            notifications = self.queryset.filter(etudiant_id=etudiant_id)
            serializer = self.get_serializer(notifications, many=True)
            return Response(serializer.data)
        else:
            return super().list(request)

