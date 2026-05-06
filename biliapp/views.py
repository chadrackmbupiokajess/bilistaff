from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Categorie, Formation, Blog, Galerie, ForumSujet, ForumMessage, InscriptionFormation, ChatMessage

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
