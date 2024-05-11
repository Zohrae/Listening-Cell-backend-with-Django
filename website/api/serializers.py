from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from ..models import Visiteur, Etudiant, Administrateur, Conseiller, Demande, Notification, NotificationEtudiant
from rest_framework import serializers
from bson import ObjectId




class VisiteurSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visiteur
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom')

class ÉtudiantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Etudiant
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom', 'CNE', 'CIN', 'age')

class ConseillerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conseiller
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom', 'department', 'Instagram', 'Linkedin', 'Gmail')

class AdministrateurSerializer(serializers.ModelSerializer):

    class Meta:
        model = Administrateur
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom')

class DemandeSerializer(serializers.ModelSerializer):
    conseiller = serializers.PrimaryKeyRelatedField(queryset=Conseiller.objects.all())
    etudiant = serializers.PrimaryKeyRelatedField(queryset=Etudiant.objects.all())


    class Meta:
        model = Demande
        fields = ['id', 'title', 'conseiller', 'etudiant', 'description', 'etat']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'conseiller', 'message', 'created_at']



class NotificationEtudiantSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEtudiant
        fields = ['id', 'etudiant', 'message']




































