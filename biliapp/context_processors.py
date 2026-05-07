from .models import Message # Importez le modèle Message
# from .models import Notification # Supposons que vous ayez un modèle Notification

def notification_and_message_counts(request):
    notification_count = 0
    message_count = 0

    if request.user.is_authenticated:
        # Pour les notifications, nous laissons une valeur factice pour l'instant
        # car nous n'avons pas encore de modèle Notification réel.
        notification_count = 2 # Exemple: 2 notifications non lues

        # Récupération du nombre de messages non lus pour l'utilisateur connecté
        try:
            message_count = Message.objects.filter(recipient=request.user, read=False).count()
        except Exception:
            # En cas d'erreur (par exemple, si la table n'est pas encore prête), on retourne 0
            message_count = 0

    return {
        'notification_count': notification_count,
        'message_count': message_count,
    }
