from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max # Importez Max pour les requêtes agrégées
from .models import Categorie, Formation, InscriptionFormation, Blog, Galerie, ForumSujet, ForumMessage, ChatMessage, Message # Importez le modèle Message

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
    # Récupère tous les messages reçus par l'utilisateur actuel, triés par date
    all_received_messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')

    # Dictionnaire pour stocker les messages groupés par expéditeur
    # {sender_id: {'sender': User, 'latest_message': Message, 'unread_count': int}}
    grouped_messages = {}

    for msg in all_received_messages:
        sender_id = msg.sender.id
        if sender_id not in grouped_messages:
            # Si c'est le premier message de cet expéditeur, c'est le plus récent
            grouped_messages[sender_id] = {
                'sender': msg.sender,
                'latest_message': msg,
                'unread_count': 0
            }
        # Incrémente le compteur de non lus si le message n'est pas lu
        if not msg.read:
            grouped_messages[sender_id]['unread_count'] += 1

    # Convertit le dictionnaire en liste et trie par la date du dernier message
    messages_by_sender = sorted(
        grouped_messages.values(),
        key=lambda x: x['latest_message'].timestamp,
        reverse=True
    )

    return render(request, 'messages.html', {
        'messages_by_sender': messages_by_sender,
    })
