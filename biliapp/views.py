from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max, Q # Importez Max et Q pour les requêtes agrégées et complexes
from django.contrib.auth.models import User # Importez le modèle User
from django.views.generic.edit import CreateView
from django.views.generic import DetailView # Importez DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from django.http import JsonResponse # Importez JsonResponse

from .models import Categorie, Formation, InscriptionFormation, Blog, Galerie, ForumSujet, ForumMessage, ChatMessage, Message, DiscussionGroup, GroupMessage
from .forms import DiscussionGroupForm # Importez le formulaire

def home(request):
    recent_formations = Formation.objects.all().order_by('-date_creation')[:3]
    recent_blogs = Blog.objects.all().order_by('-date_publication')[:3]
    categories = Categorie.objects.all()
    return render(request, 'index.html', {
        'recent_formations': recent_formations,
        'recent_blogs': recent_blogs,
        'categories': categories
    })

def formation_list(request):
    query = request.GET.get('q')
    cat_slug = request.GET.get('categorie')
    formations = Formation.objects.all()
    categories = Categorie.objects.all()
    if query:
        formations = formations.filter(titre__icontains=query)
    if cat_slug:
        formations = formations.filter(categorie__slug=cat_slug)
    return render(request, 'formations.html', {'formations': formations, 'categories': categories})

def formation_detail(request, slug):
    formation = get_object_or_404(Formation, slug=slug)
    programme_list = [line.strip() for line in formation.programme.split('\n') if line.strip()]

    deja_inscrit = False
    if request.user.is_authenticated:
        deja_inscrit = InscriptionFormation.objects.filter(user=request.user, formation=formation).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        modalite = request.POST.get('modalite')
        if not deja_inscrit:
            InscriptionFormation.objects.create(
                user=request.user,
                formation=formation,
                modalite=modalite
            )
            messages.success(request, f"Votre inscription à la formation '{formation.titre}' en mode {modalite} a été enregistrée. Elle sera validée prochainement.")
            return redirect('formation_detail', slug=slug)

    return render(request, 'formation_detail.html', {
        'formation': formation,
        'programme_list': programme_list,
        'deja_inscrit': deja_inscrit
    })

def blog_list(request):
    blogs = Blog.objects.all().order_by('-date_publication')
    return render(request, 'blog.html', {'blogs': blogs})

def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    suggestions = Blog.objects.exclude(pk=pk)[:3]
    return render(request, 'blog_detail.html', {'blog': blog, 'suggestions': suggestions})

def galerie_list(request):
    images = Galerie.objects.all().order_by('-date_ajout')
    return render(request, 'galerie.html', {'images': images})

@login_required
def forum(request):
    sujets = ForumSujet.objects.all().order_by('-date_creation')
    if request.method == 'POST':
        titre = request.POST.get('titre')
        if titre:
            ForumSujet.objects.create(titre=titre, auteur=request.user)
            return redirect('forum')
    return render(request, 'forum.html', {'sujets': sujets})

@login_required
def forum_detail(request, pk):
    sujet = get_object_or_404(ForumSujet, pk=pk)
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            ForumMessage.objects.create(sujet=sujet, auteur=request.user, contenu=contenu)
            return redirect('forum_detail', pk=pk)
    return render(request, 'forum_detail.html', {'sujet': sujet})

@login_required
def chat_view(request):
    messages_chat = ChatMessage.objects.all().order_by('-timestamp')[:50]
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(user=request.user, message=message_text)
            return redirect('chat')
    return render(request, 'chat.html', {'chat_messages': reversed(messages_chat)})

def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/connexion.html', {'form': form})

def deconnexion(request):
    logout(request)
    return redirect('home')

def a_propos(request):
    return render(request, 'a_propos.html')

@login_required
def notifications_view(request):
    # Ici, tu récupérerais les vraies notifications pour l'utilisateur
    # Pour l'exemple, nous allons simuler quelques notifications
    notifications = [
        {'id': 1, 'message': 'Nouvelle formation disponible : Python Avancé', 'read': False},
        {'id': 2, 'message': 'Votre inscription à "Django pour débutants" a été validée.', 'read': True},
        {'id': 3, 'message': 'Quelqu\'un a répondu à votre sujet sur le forum.', 'read': False},
    ]
    
    # Compte les notifications non lues
    notification_count = sum(1 for n in notifications if not n['read'])

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'notification_count': notification_count
    })

@login_required
def messages_view(request):
    search_query = request.GET.get('q')

    # Récupère tous les messages reçus par l'utilisateur actuel, triés par date
    all_received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')

    # Dictionnaire pour stocker les messages groupés par expéditeur
    grouped_messages = {}

    for msg in all_received_messages:
        sender_id = msg.sender.id
        if sender_id not in grouped_messages:
            grouped_messages[sender_id] = {
                'sender': msg.sender,
                'latest_message': msg,
                'unread_count': 0
            }
        if not msg.read:
            grouped_messages[sender_id]['unread_count'] += 1

    messages_by_sender = sorted(
        grouped_messages.values(),
        key=lambda x: x['latest_message'].timestamp,
        reverse=True
    )

    # Récupérer les groupes de discussion dont l'utilisateur est membre
    user_groups = request.user.discussion_groups.all()
    group_conversations = []
    for group in user_groups:
        latest_group_message = group.messages.order_by('-timestamp').first()
        if latest_group_message:
            group_conversations.append({
                'group': group,
                'latest_message': latest_group_message,
                # Pour les groupes, on ne gère pas de "non lus" de la même manière que les messages privés
                # On pourrait ajouter une logique plus tard si nécessaire
                'unread_count': 0 
            })
        else:
            group_conversations.append({
                'group': group,
                'latest_message': None,
                'unread_count': 0
            })
    
    # Combiner les messages privés et les groupes pour l'affichage
    all_conversations = []
    for conv in messages_by_sender:
        all_conversations.append({
            'type': 'private',
            'id': conv['sender'].id,
            'name': conv['sender'].username,
            'latest_message_body': conv['latest_message'].body,
            'latest_message_timestamp': conv['latest_message'].timestamp,
            'unread_count': conv['unread_count'],
            'sender_object': conv['sender']
        })

    for conv in group_conversations:
        all_conversations.append({
            'type': 'group',
            'id': conv['group'].id,
            'name': conv['group'].name,
            'latest_message_body': conv['latest_message'].content if conv['latest_message'] else "Aucun message",
            'latest_message_timestamp': conv['latest_message'].timestamp if conv['latest_message'] else conv['group'].created_at,
            'unread_count': conv['unread_count'],
            'group_object': conv['group']
        })

    # Trier toutes les conversations par le timestamp du dernier message
    all_conversations.sort(key=lambda x: x['latest_message_timestamp'], reverse=True)


    # Appliquer le filtre de recherche si une requête est présente
    if search_query:
        filtered_all_conversations = []
        for conversation in all_conversations:
            if search_query.lower() in conversation['name'].lower() or \
               search_query.lower() in conversation['latest_message_body'].lower():
                filtered_all_conversations.append(conversation)
        all_conversations = filtered_all_conversations


    return render(request, 'messages.html', {
        'all_conversations': all_conversations,
    })

@login_required
def message_detail_view(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)

    # Récupérer tous les messages entre l'utilisateur connecté et other_user
    messages_conversation = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp') # Trier par ordre chronologique

    # Marquer comme lus les messages reçus de cet other_user
    Message.objects.filter(sender=other_user, recipient=request.user, read=False).update(read=True)

    if request.method == 'POST':
        body = request.POST.get('body')
        if body:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                body=body
            )
            # Rediriger pour éviter la soumission multiple du formulaire
            return redirect('message_detail', user_id=user_id)

    return render(request, 'message_detail.html', {
        'other_user': other_user,
        'messages_conversation': messages_conversation,
    })

class DiscussionGroupCreateView(UserPassesTestMixin, CreateView):
    model = DiscussionGroup
    form_class = DiscussionGroupForm
    template_name = 'biliapp/create_discussion_group.html'
    success_url = reverse_lazy('discussion_group_list') # Rediriger vers la liste des groupes après création

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        form.instance.admin = self.request.user # L'utilisateur connecté est l'administrateur du groupe
        response = super().form_valid(form)
        
        # Ajouter l'administrateur aux membres du groupe
        self.object.members.add(self.request.user)
        
        # Ajouter les membres sélectionnés dans le formulaire
        selected_members = form.cleaned_data.get('members')
        if selected_members:
            self.object.members.add(*selected_members)
        
        messages.success(self.request, "Le groupe de discussion a été créé avec succès.")
        return response

@login_required
def discussion_group_list(request):
    groups = DiscussionGroup.objects.all().order_by('name')
    return render(request, 'biliapp/discussion_group_list.html', {'groups': groups})

class DiscussionGroupDetailView(DetailView):
    model = DiscussionGroup
    template_name = 'biliapp/discussion_group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group_messages'] = self.object.messages.all().order_by('timestamp')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Vérifier si l'utilisateur est membre du groupe avant de poster
        if not request.user.is_authenticated or request.user not in self.object.members.all():
            messages.error(request, "Vous devez être membre de ce groupe pour envoyer un message.")
            return self.get(request, *args, **kwargs)

        content = request.POST.get('message')
        attachment = request.FILES.get('attachment') # Récupérer le fichier

        if content or attachment: # Un message doit avoir du contenu ou une pièce jointe
            GroupMessage.objects.create(
                group=self.object,
                sender=request.user,
                content=content,
                attachment=attachment # Enregistrer la pièce jointe
            )
            return redirect('discussion_group_detail', pk=self.object.pk)
        else:
            messages.error(request, "Le message ne peut pas être vide.")
            return self.get(request, *args, **kwargs) # Re-render la page avec les messages et erreurs

@login_required
def search_users_api(request):
    query = request.GET.get('q', '')
    
    found_users = User.objects.filter(
        Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ).exclude(id=request.user.id).values('id', 'username').order_by('username')

    # Limiter le nombre de résultats pour éviter de charger trop d'utilisateurs
    if not query:
        found_users = found_users[:20] # Afficher les 20 premiers utilisateurs si pas de recherche
    else:
        found_users = found_users[:10] # Limiter les résultats de recherche à 10

    users = list(found_users)
    return JsonResponse(users, safe=False)
