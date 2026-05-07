from django import forms
from .models import DiscussionGroup, User

class DiscussionGroupForm(forms.ModelForm):
    # Permet de sélectionner plusieurs membres pour le groupe
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by('username'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Membres du groupe"
    )

    class Meta:
        model = DiscussionGroup
        fields = ['name', 'description', 'members']
        labels = {
            'name': "Nom du groupe",
            'description': "Description du groupe",
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
