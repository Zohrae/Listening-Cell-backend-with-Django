from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField
from ..models import *
from rest_framework import serializers
from bson import ObjectId
from ..models import Event



class VisiteurSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visiteur
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom')

class ÉtudiantSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Etudiant
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom', 'major', 'age', 'is_valid', 'verification_code', 'image')

        


class ConseillerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Conseiller
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom', 'department', 'Instagram', 'Linkedin', 'Gmail', 'image', 'est_connecte')

class AdministrateurSerializer(serializers.ModelSerializer):

    class Meta:
        model = Administrateur
        fields = ('id', 'nomUtilisateur', 'motDePasse', 'email', 'phoneNumber', 'Nom', 'Prenom')



class DisponibiliteConseillerSerializer(serializers.ModelSerializer):
    conseiller = serializers.PrimaryKeyRelatedField(queryset=Conseiller.objects.all())

    class Meta:
        model = DisponibiliteConseiller
        fields = ['id', 'conseiller', 'date_heure']  # Champs mis à jour



class DemandeSerializer(serializers.ModelSerializer):
    conseiller = serializers.PrimaryKeyRelatedField(queryset=Conseiller.objects.all())
    etudiant = serializers.PrimaryKeyRelatedField(queryset=Etudiant.objects.all())
    class Meta:
        model = Demande
        fields = ['id', 'title', 'conseiller', 'etudiant', 'description', 'etat', 'date_heure']


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ['id', 'demande', 'observation', 'date_observation']



class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'conseiller', 'message', 'created_at', 'vu']



class NotificationEtudiantSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEtudiant
        fields = ['id', 'etudiant', 'message']





class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'nomEvenement', 'date', 'lieu', 'image')




class FeedbackSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Feedback
        fields = ['id', 'etudiant', 'contenu', 'valide_par_admin', 'valide_par_etudiant', 'date_ajout_feedback']



class DossierSerializer(ModelSerializer):
    etudiant = PrimaryKeyRelatedField(queryset=Etudiant.objects.all())
    feedbacks = FeedbackSerializer(many=True, read_only=True)
    demandes = SerializerMethodField()

    class Meta:
        model = Dossier
        fields = ['id', 'etudiant', 'feedbacks', 'demandes', 'date_ajout_dossier']

    def get_feedbacks(self, obj):
        feedbacks = Feedback.objects.filter(etudiant=obj.etudiant)
        return FeedbackSerializer(feedbacks, many=True).data

    def get_demandes(self, obj):
        demandes = Demande.objects.filter(etudiant=obj.etudiant)
        return DemandeSerializer(demandes, many=True).data


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id',
            'sender_etudiant',
            'sender_conseiller',
            'receiver_etudiant',
            'receiver_conseiller',
            'content',
            'timestamp',
            'is_read'
        ]


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = ['id', 'admin', 'message', 'created_at', 'vu']



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'NomComplet', 'EmailAuteur', 'Question', 'Reponse', 'dateAjoutDeQuestion']


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = ['id', 'contenu', 'date_ajout']


class TODOSerializer(serializers.ModelSerializer):
    class Meta:
        model = TODO
        fields = ['id', 'TODO', 'DateAjoutTODO', 'assignee_conseiller', 'assignee_etudiant']


class CollaborateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborateur
        fields = ['id', 'nom', 'prenom', 'email', 'telephone', 'entreprise_associee', 'poste_occupe']


class RessourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ressource
        fields = ['id', 'titre', 'dateAjoutRessource', 'description', 'image', 'url']
















