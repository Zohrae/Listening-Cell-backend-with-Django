from django.contrib import admin

# from .models import Utilisateur
# from .models import Department
# from .models import Major
from .models import Conseiller
from .models import Visiteur
from .models import Etudiant
from .models import Administrateur
from .models import Demande, Notification, NotificationEtudiant




admin.site.register(Demande)
admin.site.register(Conseiller)
admin.site.register(Visiteur)
admin.site.register(Etudiant)
admin.site.register(Administrateur)
admin.site.register(Notification)
admin.site.register(NotificationEtudiant)








