from django.db import models
from django.utils import timezone



class Visiteur(models.Model):

    nomUtilisateur = models.CharField(max_length=100)
    motDePasse = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)

    def register(self):
        pass

    def viewEvents(self):
        pass
    class Meta:
        db_table = 'Visiteurs'


class Etudiant(models.Model):

    nomUtilisateur = models.CharField(max_length=100)
    motDePasse = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    CNE = models.CharField(max_length=10)
    CIN = models.CharField(max_length=20)
    age = models.PositiveIntegerField()

    def scheduleAppointment(self):
        # Implementation of scheduleAppointment method
        pass

    def sendMessage(self):
        # Implementation of sendMessage method
        pass

    def submitFeedback(self):
        # Implementation of submitFeedback method
        pass

    def __str__(self):
        return f"{self.Nom} {self.Prenom}"

    class Meta:
        db_table = 'Etudiants'


class Conseiller(models.Model):
    nomUtilisateur = models.CharField(max_length=100)
    motDePasse = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    Instagram = models.CharField(max_length=100)
    Linkedin = models.CharField(max_length=100)
    Gmail = models.EmailField()


    def __str__(self):
        return f"{self.Nom} {self.Prenom}"

    class Meta:
        db_table = 'Conseillers'

class Administrateur(models.Model):
    nomUtilisateur = models.CharField(max_length=100)
    motDePasse = models.CharField(max_length=100)
    email = models.EmailField()
    phoneNumber = models.CharField(max_length=15)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)

    def addEvent(self):
        # Implementation of addEvent method
        pass

    def updateEvent(self):
        # Implementation of updateEvent method
        pass

    def deleteEvent(self):
        # Implementation of deleteEvent method
        pass

    def scheduleAppointment(self):
        # Implementation of scheduleAppointment method
        pass

    def sendMessage(self):
        # Implementation of sendMessage method
        pass

    def submitFeedback(self):
        # Implementation of submitFeedback method
        pass

    def addResource(self):
        # Implementation of addResource method
        pass

    def updateResource(self):
        # Implementation of updateResource method
        pass

    def deleteResource(self):
        # Implementation of deleteResource method
        pass

    class Meta:
        db_table = 'Administrateurs'

class Demande(models.Model):
    title = models.CharField(max_length=100)
    conseiller = models.ForeignKey(Conseiller, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    description = models.TextField()
    etat = models.CharField(max_length=20, choices=[('En attente', 'En attente'), ('Acceptée', 'Acceptée'), ('Refusée', 'Refusée')], default='En attente')


    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Demande'


class Notification(models.Model):
    conseiller = models.ForeignKey(Conseiller, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

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


