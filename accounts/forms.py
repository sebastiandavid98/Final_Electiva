from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from .models import Usuario


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Usuario'}
        ),
    )
    password = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Contrasena'}
        ),
    )


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    telefono = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'telefono',
            'rol',
            'carrera',
            'departamento',
            'password1',
            'password2',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'carrera': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data.get('telefono', '')
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'telefono', 'carrera', 'departamento']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }
