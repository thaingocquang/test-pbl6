from django.forms import ModelForm
from .models import AudioStore


class AudioForm(ModelForm):
    class Meta:
        model= AudioStore
        fields = ['record']