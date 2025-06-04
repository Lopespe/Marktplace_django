# marketplace/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from .models import Produto, PerfilComprador, PerfilVendedor, Avaliacao, RespostaVendedorAvaliacao, Category

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'estoque', 'imagem', 'category'] # Added category
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome do Produto'}),
            'descricao': forms.Textarea(attrs={'placeholder': 'Descrição detalhada'}),
            'preco': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'estoque': forms.NumberInput(attrs={'placeholder': '0', 'min': '0'}),
        }
    imagem = forms.ImageField(required=False, widget=forms.ClearableFileInput)

class FormCadastroComprador(forms.Form):
    nome = forms.CharField(label='Nome Completo', max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Nome Completo', 'required': True}))
    idade = forms.IntegerField(label='Idade', min_value=16, widget=forms.NumberInput(attrs={'placeholder': 'Idade', 'required': True}))
    cpf = forms.CharField(label='CPF', max_length=11, widget=forms.TextInput(attrs={'placeholder': 'CPF (somente números)', 'required': True, 'pattern': r'\d{11}', 'title': 'CPF deve conter 11 números.'}))
    curso = forms.CharField(label='Seu Curso', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Seu Curso', 'required': True}))
    ra = forms.CharField(label='Seu RA', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Seu RA (Registro Acadêmico)', 'required': True}))
    email = forms.EmailField(label='Seu melhor Email', widget=forms.EmailInput(attrs={'placeholder': 'Seu melhor Email', 'required': True}))
    senha = forms.CharField(label='Crie uma Senha', widget=forms.PasswordInput(attrs={'placeholder': 'Crie uma Senha', 'required': True}))
    confirmar_senha = forms.CharField(label='Confirme sua Senha', widget=forms.PasswordInput(attrs={'placeholder': 'Confirme sua Senha', 'required': True}))

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este email já está cadastrado. Por favor, use outro.")
        return email

    def clean_confirmar_senha(self):
        senha = self.cleaned_data.get("senha")
        confirmar_senha = self.cleaned_data.get("confirmar_senha")
        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")
        return confirmar_senha

class FormCadastroVendedor(forms.Form):
    nome = forms.CharField(label='Nome Completo', max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Nome Completo', 'required': True}))
    idade = forms.IntegerField(label='Idade', min_value=16, widget=forms.NumberInput(attrs={'placeholder': 'Idade', 'required': True}))
    cpf = forms.CharField(label='CPF', max_length=11, widget=forms.TextInput(attrs={'placeholder': 'CPF (somente números)', 'required': True, 'pattern': r'\d{11}', 'title': 'CPF deve conter 11 números.'}))
    curso = forms.CharField(label='Seu Curso', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Seu Curso', 'required': True}))
    ra = forms.CharField(label='Seu RA', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Seu RA (Registro Acadêmico)', 'required': True}))
    email = forms.EmailField(label='Seu melhor Email', widget=forms.EmailInput(attrs={'placeholder': 'Seu melhor Email', 'required': True}))
    senha = forms.CharField(label='Crie uma Senha', widget=forms.PasswordInput(attrs={'placeholder': 'Crie uma Senha', 'required': True}))
    confirmar_senha = forms.CharField(label='Confirme sua Senha', widget=forms.PasswordInput(attrs={'placeholder': 'Confirme sua Senha', 'required': True}))

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este email já está cadastrado. Por favor, use outro.")
        return email

    def clean_confirmar_senha(self):
        senha = self.cleaned_data.get("senha")
        confirmar_senha = self.cleaned_data.get("confirmar_senha")
        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")
        return confirmar_senha

# UserEditForm for ADMIN use (can edit all fields including groups/staff status)
class UserAdminEditForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Grupos"
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'is_staff', 'groups']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if 'groups' in self.cleaned_data:
                 user.groups.set(self.cleaned_data['groups'])
        return user

# NEW: UserEditForm for BUYER self-profile editing (cannot change staff/groups)
class UserBuyerProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # Only these fields for self-editing

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if the new email is already used by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este email já está em uso por outra conta.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # If the email changes, also update the username (since it's used as username)
        if 'email' in self.changed_data:
            user.username = user.email
        if commit:
            user.save()
        return user

# NEW: UserEditForm for SELLER self-profile editing (cannot change staff/groups)
class UserSellerProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] # Only these fields for self-editing

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if the new email is already used by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este email já está em uso por outra conta.")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        # If the email changes, also update the username (since it's used as username)
        if 'email' in self.changed_data:
            user.username = user.email
        if commit:
            user.save()
        return user

class PerfilCompradorEditForm(forms.ModelForm):
    class Meta:
        model = PerfilComprador
        fields = ['idade', 'cpf', 'curso', 'ra']

class PerfilVendedorEditForm(forms.ModelForm):
    class Meta:
        model = PerfilVendedor
        fields = ['idade', 'cpf', 'curso', 'ra']

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Deixe seu comentário sobre o produto...'}),
            'nota': forms.HiddenInput(), # Will be handled by star rating in JS
        }

class RespostaVendedorAvaliacaoForm(forms.ModelForm):
    class Meta:
        model = RespostaVendedorAvaliacao
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Digite sua resposta aqui...'}),
        }

