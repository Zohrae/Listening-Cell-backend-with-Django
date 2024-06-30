from django.db import models
from django.utils import timezone



class Utilisateur(models.Model):
    nomUtilisateur = models.CharField(max_length=100)
    motDePasse = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)
    dateJoining = models.DateTimeField(default=timezone.now)

    def register(self):
        pass

    def viewEvents(self):
        pass

    class Meta:
        abstract = True

class Visiteur(Utilisateur):

    def register(self):
        pass

    def viewEvents(self):
        pass
    class Meta:
        db_table = 'Visiteurs'


class Etudiant(Utilisateur):
    major = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    is_valid = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=4, blank=True, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)  


    def __str__(self):
        return f"{self.Nom} {self.Prenom}"

    class Meta:
        db_table = 'Etudiants'


class Conseiller(Utilisateur):
    department = models.CharField(max_length=100)
    Instagram = models.CharField(max_length=100)
    Linkedin = models.CharField(max_length=100)
    Gmail = models.EmailField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # New image field
    est_connecte = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.Nom} {self.Prenom}"

    class Meta:
        db_table = 'Conseillers'

class Administrateur(Utilisateur):

    def __str__(self):
        return f"{self.nomUtilisateur} {self.Prenom}"

    class Meta:
        db_table = 'Administrateurs'



class DisponibiliteConseiller(models.Model):
    conseiller = models.ForeignKey(Conseiller, on_delete=models.CASCADE)
    date_heure = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f"{self.conseiller.nomUtilisateur} - {self.date_heure}"

    class Meta:
        db_table = 'DisponibiliteConseillers'


class Demande(models.Model):
    title = models.CharField(max_length=100)
    conseiller = models.ForeignKey(Conseiller, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    description = models.TextField()
    etat = models.CharField(max_length=20, choices=[('En attente', 'En attente'), ('Acceptée', 'Acceptée'), ('Refusée', 'Refusée')], default='En attente')
    date_heure = models.DateTimeField(default=timezone.now)  


    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Demande'


class Observation(models.Model):
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE, related_name='observations')
    observation = models.TextField()
    date_observation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Observation for {self.demande.title} on {self.date_observation}"

    class Meta:
        db_table = 'Observations'


class Notification(models.Model):
    conseiller = models.ForeignKey(Conseiller, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    vu = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.conseiller.nomUtilisateur} - {self.message}"

    class Meta:
        db_table = 'Notifications'


class NotificationEtudiant(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.etudiant.nomUtilisateur} - {self.message}"

    class Meta:
        db_table = 'Notifications_Etudiant'



class Feedback(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, null=True, blank=True)
    contenu = models.TextField()
    valide_par_admin = models.BooleanField(default=False)
    valide_par_etudiant = models.BooleanField(default=False)
    date_ajout_feedback = models.DateTimeField(default=timezone.now)  # Champ de date avec date actuelle par défaut

    def __str__(self):
        return f"Feedback from {self.etudiant} to {self.conseiller}"

    class Meta:
        db_table = 'Feedbacks'
    


class Event(models.Model):
    ETAT_CHOICES = [
        ('completed', 'Completed'),
        ('ongoing', 'Ongoing'),
        ('upcoming', 'Upcoming'),
    ]
    
    nomEvenement = models.CharField(max_length=100)
    date = models.DateTimeField()
    lieu = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', null=True, blank=True)  # New image field
    etat = models.CharField(max_length=10, choices=ETAT_CHOICES, default='upcoming')
    etudiants = models.ManyToManyField('Etudiant', related_name='events')

    def __str__(self):
        return self.nomEvenement

    class Meta:
        db_table = 'Events'




class Dossier(models.Model):
    etudiant = models.OneToOneField(Etudiant, on_delete=models.CASCADE)
    feedbacks = models.ManyToManyField(Feedback, blank=True)
    demandes = models.ManyToManyField(Demande, blank=True)
    date_ajout_dossier = models.DateTimeField(auto_now_add=True)  # Automatically set date on creation

    def __str__(self):
        return f"Dossier for {self.etudiant.Nom} {self.etudiant.Prenom}"

    class Meta:
        db_table = 'Dossiers'



class Message(models.Model):
    sender_etudiant = models.ForeignKey(Etudiant, null=True, blank=True, on_delete=models.CASCADE, related_name='sent_messages')
    sender_conseiller = models.ForeignKey(Conseiller, null=True, blank=True, on_delete=models.CASCADE, related_name='sent_messages')
    receiver_etudiant = models.ForeignKey(Etudiant, null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages')
    receiver_conseiller = models.ForeignKey(Conseiller, null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        sender = self.sender_etudiant if self.sender_etudiant else self.sender_conseiller
        receiver = self.receiver_etudiant if self.receiver_etudiant else self.receiver_conseiller
        return f"From {sender} to {receiver} at {self.timestamp}"

    class Meta:
        db_table = 'Messages'
        ordering = ['timestamp']


class Alert(models.Model):
    admin = models.ForeignKey(Administrateur, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    vu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.admin.nomUtilisateur} - {self.message}"

    class Meta:
        db_table = 'Alerts'


class Question(models.Model):
    NomComplet = models.CharField(max_length=255)
    EmailAuteur = models.EmailField()
    Question = models.TextField()
    Reponse = models.TextField(null=True, blank=True)
    dateAjoutDeQuestion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Questions'

    def __str__(self):
        return self.Question



class Quote(models.Model):
    contenu = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Quotes'


class TODO(models.Model):
    TODO = models.CharField(max_length=255)
    DateAjoutTODO = models.DateTimeField(default=timezone.now)
    assignee_conseiller = models.ForeignKey('Conseiller', on_delete=models.CASCADE, null=True, blank=True)
    assignee_etudiant = models.ForeignKey('Etudiant', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.TODO

    class Meta:
        db_table = 'TODOs'



class Collaborateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=15)
    entreprise_associee = models.CharField(max_length=100)
    poste_occupe = models.CharField(max_length=100)

    class Meta:
        db_table = 'Collaborateurs'
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"



class Ressource(models.Model):
    titre = models.CharField(max_length=100)
    dateAjoutRessource = models.DateField() 
    description = models.TextField()  
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    url = models.URLField(max_length=200, null=True, blank=True)  

    def __str__(self):
        return self.titre

    class Meta:
        db_table = 'Ressources'
