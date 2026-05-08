from django.contrib import admin
from .models import Categorie, Formation, InscriptionFormation, Blog, Galerie, ForumSujet, ForumMessage, ChatMessage, Message, DiscussionGroup, GroupMessage # Importez le modèle GroupMessage

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

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'get_body_excerpt', 'timestamp', 'read') # 'subject' remplacé par 'get_body_excerpt'
    list_filter = ('read', 'timestamp', 'sender', 'recipient')
    search_fields = ('body', 'sender__username', 'recipient__username') # 'subject' remplacé par 'body'
    actions = ['mark_as_read', 'mark_as_unread']

    def get_body_excerpt(self, obj):
        return obj.body[:75] + '...' if len(obj.body) > 75 else obj.body
    get_body_excerpt.short_description = "Contenu" # Nom de la colonne dans l'admin

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Marquer les messages sélectionnés comme lus"

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
    mark_as_unread.short_description = "Marquer les messages sélectionnés comme non lus"

@admin.register(DiscussionGroup)
class DiscussionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'created_at')
    list_filter = ('admin', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',) # Permet une meilleure gestion des ManyToMany dans l'admin

@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'content', 'timestamp')
    list_filter = ('group', 'sender', 'timestamp')
    search_fields = ('group__name', 'sender__username', 'content')
