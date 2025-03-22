from django import forms
from .models import UDN, Sector, IssueCategory, Issue

class TicketCreationForm(forms.Form):
    udn = forms.ModelChoiceField(queryset=UDN.objects.all(), label="UDN")
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), label="Sector")
    issue_category = forms.ModelChoiceField(queryset=IssueCategory.objects.all(), label="Categoría")
    issue = forms.ModelChoiceField(queryset=Issue.objects.all(), label="Incidencia")
    body = forms.CharField(widget=forms.Textarea, required=False, label="Descripción")



class AttachmentForm(forms.Form):
    """
    Formulario para validar archivos adjuntos.
    Este formulario se usa para validar los archivos adjuntos que se envían con un ticket.
    """
    file = forms.FileField(label="Archivo")
    filename = forms.CharField(max_length=255, label="Nombre del archivo")
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Tamaño máximo: 50MB (52428800 bytes)
            if file.size > 52428800:
                raise forms.ValidationError("El archivo no puede superar los 50MB.")
        return file