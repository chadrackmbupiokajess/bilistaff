from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def time_ago(value):
    now = timezone.now()
    diff = now - value

    if diff.days == 0:
        if diff.seconds < 60:
            return "à l'instant"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            hours = diff.seconds // 3600
            return f"il y a {hours} heure{'s' if hours > 1 else ''}"
    elif diff.days == 1:
        return "hier"
    elif diff.days < 7:
        return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"il y a {weeks} semaine{'s' if weeks > 1 else ''}"
    elif diff.days < 365:
        months = diff.days // 30
        return f"il y a {months} mois"
    else:
        years = diff.days // 365
        return f"il y a {years} an{'s' if years > 1 else ''}"
