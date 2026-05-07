from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from biliapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('formations/', views.formation_list, name='formations'),
    path('formations/<slug:slug>/', views.formation_detail, name='formation_detail'),
    path('blog/', views.blog_list, name='blog'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('galerie/', views.galerie_list, name='galerie'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('forum/', views.forum, name='forum'),
    path('forum/<int:pk>/', views.forum_detail, name='forum_detail'),
    path('chat/', views.chat_view, name='chat'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('messages/', views.messages_view, name='messages'), # Nouvelle URL pour les messages
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
