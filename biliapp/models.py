from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='fas fa-code', help_text="Classe FontAwesome")

    def __str__(self):
        return self.nom

class Formation(models.Model):
    NIVEAU_CHOICES = [
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
    ]
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, null=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='formations')
    description = models.TextField()
    programme = models.TextField(help_text="Utilisez des tirets pour chaque point", blank=True)
    image = models.ImageField(upload_to='formations/', blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    # On garde ces champs pour indiquer les disponibilités générales de la formation
    disponible_en_ligne = models.BooleanField(default=True)
    disponible_presentiel = models.BooleanField(default=True)
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='Débutant')
    duree = models.CharField(max_length=50, blank=True, help_text="Ex: 10 heures")
    date_creation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

class InscriptionFormation(models.Model):
    MODALITE_CHOICES = [
        ('en_ligne', 'En ligne'),
        ('presentiel', 'Présentiel'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    modalite = models.CharField(max_length=20, choices=MODALITE_CHOICES, default='en_ligne')
    date_inscription = models.DateTimeField(auto_now_add=True)
    est_valide = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'formation')

    def __str__(self):
        return f"{self.user.username} - {self.formation.titre} ({self.get_modalite_display()})"

class Blog(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class Galerie(models.Model):
    image = models.ImageField(upload_to='galerie/')
    description = models.CharField(max_length=200, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description or f"Image {self.id}"

class ForumSujet(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class ForumMessage(models.Model):
    sujet = models.ForeignKey(ForumSujet, related_name='messages', on_delete=models.CASCADE)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message de {self.auteur.username} sur {self.sujet.titre}"

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp'] # Les messages les plus récents en premier

    def __str__(self):
        return f"De {self.sender.username} à {self.recipient.username}: {self.subject[:50]}"
