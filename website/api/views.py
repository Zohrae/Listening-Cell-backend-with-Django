from rest_framework.viewsets import ModelViewSet
from rest_framework import status , generics
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth import login as django_login
import json
from django.http import JsonResponse, request, StreamingHttpResponse
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail, EmailMessage
import random
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from rest_framework.decorators import action
from transformers import pipeline
from django.utils.dateparse import parse_datetime
from collections import defaultdict
import calendar
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import time
from django.db.models import Count

from asgiref.sync import async_to_sync
import spacy
from spacy.matcher import PhraseMatcher
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from ..models import *
from .serializers import *



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

    
    def send_email(self, subject, message, recipient_list):
        sender_email = settings.EMAIL_HOST_USER
        receiver_email = recipient_list

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ', '.join(receiver_email)
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            email = serializer.validated_data['email']

            random_code = f"{random.randint(1000, 9999)}"
            message = f"Your verification code is: {random_code}"
            subject = 'Verification Code'
            recipient_list = [email]
            self.send_email(subject, message, recipient_list)

            etudiant = Etudiant.objects.get(pk=serializer.data['id'])
            etudiant.verification_code = random_code
            etudiant.save()

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        try:
            etudiant = Etudiant.objects.get(nomUtilisateur=pk)
        except Etudiant.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        verification_code = request.data.get('verification_code')
        if verification_code == etudiant.verification_code:
            etudiant.is_valid = True
            etudiant.verification_code = ''
            etudiant.save()
            return Response({'detail': 'Verification successful.'})
        else:
            return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        verification_code = request.data.get('verification_code')
        if verification_code and verification_code == instance.verification_code:
            instance.is_valid = True
            instance.save()

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def count_by_month_2024(self, request):
        students_2024 = Etudiant.objects.filter(dateJoining__year=2024)
        count_by_month = defaultdict(int)
        
        for student in students_2024:
            month = student.dateJoining.month
            count_by_month[month] += 1
        
        result = {calendar.month_name[month]: count for month, count in count_by_month.items()}
        
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def with_requests(self, request):
        conseiller_id = request.query_params.get('conseiller_id')
        if not conseiller_id:
            return Response({'detail': 'Conseiller ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        students_with_requests = Etudiant.objects.filter(demande__conseiller_id=conseiller_id).distinct()
        serializer = self.get_serializer(students_with_requests, many=True)
        return Response(serializer.data)

    
    @action(detail=False, methods=['get'])
    def count_by_major(self, request):
        counts = Etudiant.objects.values('major').annotate(total=Count('major'))
        return Response(counts)

    @action(detail=False, methods=['get'])
    def count_etudiants(self, request):
        student_count = Etudiant.objects.count()
        return Response({'student_count': student_count})
    

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

                conseiller.est_connecte = True
                conseiller.save()

                return JsonResponse({'id': conseiller.id}, status=200)

            except Conseiller.DoesNotExist:
                return JsonResponse({'detail': 'Invalid username or password.'}, status=401)
        else:
            return JsonResponse({'detail': 'Invalid request data.'}, status=400)
    return render(request, 'login.html')


def success(request):
    return render(request, 'success.html')

@csrf_exempt
def logout_user(request):
    if request.method == 'POST':
        conseiller_id = request.session.get('conseiller_id')
        
        if conseiller_id:
            conseiller = Conseiller.objects.get(id=conseiller_id)
            conseiller.est_connecte = False
            conseiller.save()

        request.session.flush()

        return JsonResponse({'detail': 'Logout successful'}, status=200)
    else:
        return JsonResponse({'detail': 'Invalid request method.'}, status=400)




@csrf_exempt
def login_etudiant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid request data.'}, status=400)

        if username is not None and password is not None:
            try:
                etudiant = Etudiant.objects.get(nomUtilisateur=username, motDePasse=password)
                if not etudiant.is_valid:
                    return JsonResponse({'detail': 'Veuillez activer votre compte.'}, status=403)
                
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



@csrf_exempt
def login_admin(request):
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
                admin = Administrateur.objects.get(nomUtilisateur=username, motDePasse=password)
                request.session['username'] = username
                request.session['admin_id'] = admin.id

                return JsonResponse({'id': admin.id}, status=200)

            except Conseiller.DoesNotExist:
                return JsonResponse({'detail': 'Invalid username or password.'}, status=401)
        else:
            return JsonResponse({'detail': 'Invalid request data.'}, status=400)
    return render(request,)



class DisponibiliteConseillerViewSet(ModelViewSet):
    queryset = DisponibiliteConseiller.objects.all()
    serializer_class = DisponibiliteConseillerSerializer

    def list(self, request):
        conseiller_id = request.query_params.get('conseiller')

        if conseiller_id:
            dispos = self.queryset.filter(conseiller_id=conseiller_id)
            serializer = self.get_serializer(dispos, many=True)
            return Response(serializer.data)
        else:
            return super().list(request)

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
        etudiant_id = request.query_params.get('etudiant')
        etats = request.query_params.get('etat')

        demandes = self.queryset

        if conseiller_id:
            demandes = demandes.filter(conseiller_id=conseiller_id)
        if etudiant_id:
            demandes = demandes.filter(etudiant_id=etudiant_id)
        if etats:
            etats_list = etats.split(',')
            demandes = demandes.filter(etat__in=etats_list)

        serializer = self.get_serializer(demandes, many=True)
        return Response(serializer.data)


class ObservationViewSet(ModelViewSet):
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

    def list(self, request):
        demande_id = request.query_params.get('demande')

        if demande_id:
            observations = self.queryset.filter(demande_id=demande_id)
            serializer = self.get_serializer(observations, many=True)
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



class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            valide_par_admin = request.data.get('valide_par_admin', False) == 'true'
            valide_par_etudiant = request.data.get('valide_par_etudiant', False) == 'true'

            feedback = Feedback.objects.create(
                etudiant_id=request.data.get('etudiant'),
                contenu=request.data.get('contenu'),
                valide_par_admin=valide_par_admin,
                valide_par_etudiant=valide_par_etudiant
            )

            self.update_dossier(feedback.etudiant)

            serializer = self.get_serializer(feedback)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_dossier(self, etudiant):
        try:
            dossier = Dossier.objects.get(etudiant=etudiant)
            feedbacks = Feedback.objects.filter(etudiant=etudiant)
            dossier.feedbacks.set(feedbacks)
            dossier.save()
        except Dossier.DoesNotExist:
            pass  # Handle case where dossier does not exist if necessary

        
    def list(self, request):
        etudiant_id = request.query_params.get('etudiant')

        if etudiant_id:
            feedbacks = self.queryset.filter(etudiant_id=etudiant_id)
            serializer = self.get_serializer(feedbacks, many=True)
            return Response(serializer.data)
        else:
            return super().list(request)
    
    @action(detail=False, methods=['get'])
    def analyzeAll(self, request):
        feedbacks = Feedback.objects.all()
        feedback_data = []

        sentiment_analysis = pipeline('sentiment-analysis', model="nlptown/bert-base-multilingual-uncased-sentiment")

        for feedback in feedbacks:
            analysis_result = sentiment_analysis(feedback.contenu)[0]
            score_label = analysis_result['label']
            score = int(score_label.split()[0]) - 3  # Extract numeric part and convert label (1-5) to (-2 to 2)
            feedback_data.append({
                'id': feedback.id,
                'sentiment': score,
                'content': feedback.contenu
            })

        return Response(feedback_data)


    @action(detail=False, methods=['get'])
    def analyze(self, request):
        etudiant_id = request.query_params.get('etudiant')
        if not etudiant_id:
            return Response({'error': 'Etudiant ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        feedbacks = self.queryset.filter(etudiant_id=etudiant_id)
        feedbacks_data = self.get_serializer(feedbacks, many=True).data
        
        sentiment_pipeline = pipeline('sentiment-analysis', model="nlptown/bert-base-multilingual-uncased-sentiment")
        sentiments = []

        for feedback in feedbacks_data:
            result = sentiment_pipeline(feedback['contenu'])[0]
            score_mapping = {
                '1 star': -2,
                '2 stars': -1,
                '3 stars': 0,
                '4 stars': 1,
                '5 stars': 2
            }
            score = score_mapping[result['label']]
            sentiments.append({
                'feedback_id': feedback['id'],
                'score': score
            })

        return Response(sentiments)

    @action(detail=False, methods=['get'])
    def count_feedback(self, request):
        etudiant_id = request.query_params.get('etudiant')
        if etudiant_id:
            feedback_count = Feedback.objects.filter(etudiant_id=etudiant_id).count()
        else:
            feedback_count = Feedback.objects.count()
        return Response({'feedback_count': feedback_count})


    
class QuoteViewSet(ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer

    @action(detail=False, methods=['get'])
    def random_quote(self, request):
        quotes = Quote.objects.all()
        random_quote = random.choice(quotes)
        serializer = self.get_serializer(random_quote)
        return Response(serializer.data)

    
    
class DossierViewSet(ModelViewSet):
    queryset = Dossier.objects.all()
    serializer_class = DossierSerializer

    def create(self, request, *args, **kwargs):
        etudiant_id = request.data.get('etudiant')
        etudiant = get_object_or_404(Etudiant, id=etudiant_id)
        
        dossier, created = Dossier.objects.get_or_create(etudiant=etudiant)
        
        feedbacks = Feedback.objects.filter(etudiant=etudiant)
        demandes = Demande.objects.filter(etudiant=etudiant)
        
        dossier.feedbacks.set(feedbacks)
        dossier.demandes.set(demandes)
        
        serializer = self.get_serializer(dossier)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['get'])
    def count_by_month(self, request):
        dossiers_2024 = Dossier.objects.filter(date_ajout_dossier__year=2024)
        count_by_month = defaultdict(int)
        
        for dossier in dossiers_2024:
            month = dossier.date_ajout_dossier.month
            count_by_month[month] += 1
        
        result = {calendar.month_name[month]: count for month, count in count_by_month.items()}
        
        return Response(result, status=status.HTTP_200_OK)

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @action(detail=False, methods=['get'])
    def for_conseiller(self, request):
        conseiller_id = request.query_params.get('conseiller_id')
        messages = Message.objects.filter(receiver_conseiller_id=conseiller_id, sender_etudiant_id=request.user.id)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def for_etudiant(self, request):
        etudiant_id = request.query_params.get('etudiant_id')
        messages = Message.objects.filter(
            receiver_etudiant_id=etudiant_id, 
            sender_conseiller_id=request.query_params.get('conseiller_id')  # Conserver sender_conseiller_id
        ) | Message.objects.filter(
            sender_etudiant_id=etudiant_id, 
            receiver_conseiller_id=request.query_params.get('conseiller_id')
        )
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def analyze_motivation(self, request):
        etudiant_id = request.query_params.get('etudiant_id')
        messages = Message.objects.filter(
            receiver_etudiant_id=etudiant_id, 
            sender_conseiller_id=request.query_params.get('conseiller_id')  
        ) | Message.objects.filter(
            sender_etudiant_id=etudiant_id, 
            receiver_conseiller_id=request.query_params.get('conseiller_id')
        )

        motivation_needed = self.analyze_messages_for_motivation(messages)

        return Response({'motivation_needed': motivation_needed})

    def analyze_messages_for_motivation(self, messages):
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-multilingual-cased')
        model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-multilingual-cased')

        education_keywords = ["école", "études", "cours", "examen", "notes", "devoirs"]
        family_keywords = ["famille", "parents", "frères et sœurs", "parents"]
        work_keywords = ["travail", "emploi", "carrière", "boulot"]

        motivation = {'education': False, 'family': False, 'work': False}
        for msg in messages:
            inputs = tokenizer(msg.content, return_tensors="pt", max_length=512, truncation=True)
            outputs = model(**inputs)
            predicted_class = torch.argmax(outputs.logits).item()
            if predicted_class == 0:
                motivation['education'] = True
            elif predicted_class == 1:
                motivation['family'] = True
            elif predicted_class == 2:
                motivation['work'] = True

        return motivation
    


class AlertViewSet(ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer

    def list(self, request):
        admin_id = request.query_params.get('admin')

        if admin_id:
            alerts = self.queryset.filter(admin_id=admin_id)
            serializer = self.get_serializer(alerts, many=True)
            return Response(serializer.data)
        else:
            return super().list(request)

        

class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


    @action(detail=False, methods=['get'])
    def classifyQuestions(self, request):
        all_questions = Question.objects.all().values_list('Question', flat=True)

        tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        model = BertForSequenceClassification.from_pretrained('bert-base-multilingual-cased', num_labels=2)

        encoded_inputs = tokenizer(all_questions, padding=True, truncation=True, return_tensors='pt')

        with torch.no_grad():
            outputs = model(**encoded_inputs)

        probabilities = torch.softmax(outputs.logits, dim=1)

        average_probabilities = probabilities[:, 1].numpy().mean(axis=1)

        sorted_indices = average_probabilities.argsort()[::-1]
        most_common_questions = [all_questions[i] for i in sorted_indices]

        return Response({"most_common_questions": most_common_questions})



class TODOViewSet(ModelViewSet):
    queryset = TODO.objects.all()
    serializer_class = TODOSerializer

    @action(detail=False, methods=['get'], url_path='etudiant/(?P<etudiant_id>[^/.]+)')
    def get_todos_by_etudiant(self, request, etudiant_id=None):
        todos = TODO.objects.filter(assignee_etudiant_id=etudiant_id)
        serializer = self.get_serializer(todos, many=True)
        return Response(serializer.data)


class CollaborateurViewSet(ModelViewSet):
    queryset = Collaborateur.objects.all()
    serializer_class = CollaborateurSerializer


class RessourceViewSet(ModelViewSet):
    queryset = Ressource.objects.all()
    serializer_class = RessourceSerializer
