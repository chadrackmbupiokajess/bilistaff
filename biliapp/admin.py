from django.contrib import admin
from .models import Categorie, Formation, InscriptionFormation, Blog, Galerie, ForumSujet, ForumMessage, ChatMessage

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'icon')
    prepopulated_fields = {'slug': ('nom',)}

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'categorie', 'prix', 'niveau', 'disponible_en_ligne', 'disponible_presentiel')
    list_filter = ('categorie', 'niveau', 'disponible_en_ligne', 'disponible_presentiel')
    search_fields = ('titre', 'description')
    prepopulated_fields = {'slug': ('titre',)}

@admin.register(InscriptionFormation)
class InscriptionFormationAdmin(admin.ModelAdmin):
    list_display = ('user', 'formation', 'modalite', 'date_inscription', 'est_valide')
    list_filter = ('modalite', 'est_valide', 'formation')
    search_fields = ('user__username', 'formation__titre')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_publication')
    list_filter = ('auteur', 'date_publication')
    search_fields = ('titre', 'contenu')

@admin.register(Galerie)
class GalerieAdmin(admin.ModelAdmin):
    list_display = ('description', 'date_ajout')
    list_filter = ('date_ajout',)

class ForumMessageInline(admin.TabularInline):
    model = ForumMessage
    extra = 1

@admin.register(ForumSujet)
class ForumSujetAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'date_creation')
    list_filter = ('auteur', 'date_creation')
    search_fields = ('titre',)
    inlines = [ForumMessageInline]

@admin.register(ForumMessage)
class ForumMessageAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'sujet', 'date_envoi')
    list_filter = ('auteur', 'date_envoi')
    search_fields = ('contenu',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('message',)
