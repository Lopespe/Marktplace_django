# marketplace/models.py
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=50, blank=True, null=True, help_text="Font Awesome icon class, e.g., 'fas fa-pizza-slice'") # For frontend display
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class PerfilComprador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_comprador')
    idade = models.PositiveIntegerField(null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    curso = models.CharField(max_length=100, null=True, blank=True)
    ra = models.CharField(max_length=20, null=True, blank=True)
    desejos = models.ManyToManyField('Produto', related_name='compradores_desejam', blank=True) # Added wishlist

    def __str__(self):
        return f"Perfil de {self.user.username}"

class PerfilVendedor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_vendedor')
    idade = models.PositiveIntegerField(null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    curso = models.CharField(max_length=100, null=True, blank=True)
    ra = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"Perfil de Vendedor: {self.user.username}"

class Produto(models.Model):
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products') # Added category

    def __str__(self):
        return f"{self.nome} - {self.vendedor.username}"

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('preparando', 'Preparando'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos_vendidos')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compras')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_pedido = models.DateTimeField(auto_now_add=True)

    @property
    def total_pedido(self):
        return self.produto.preco * self.quantidade

    def __str__(self):
        return f"Pedido #{self.pk} - {self.produto.nome} ({self.quantidade}) por {self.cliente.username}"

class Avaliacao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='avaliacoes')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    nota = models.PositiveIntegerField(default=5)
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.cliente.username} para {self.produto.nome} (Nota: {self.nota})"

class RespostaVendedorAvaliacao(models.Model):
    avaliacao = models.OneToOneField(Avaliacao, on_delete=models.CASCADE, related_name='resposta_do_vendedor')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='respostas_dadas_avaliacoes')
    texto = models.TextField()
    data_resposta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resposta de {self.vendedor.username} para avaliação #{self.avaliacao.id}"

class Reporte(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_analise', 'Em Análise'),
        ('resolvido_aprovado', 'Resolvido (Ação Tomada)'),
        ('resolvido_rejeitado', 'Resolvido (Rejeitado)'),
        ('arquivado', 'Arquivado'),
    ]

    usuario_reportou = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes_feitos')
    produto_reportado = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes_sobre_este_produto')
    usuario_alvo_reporte = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reportes_recebidos_como_alvo')
    titulo = models.CharField(max_length=255, help_text="Um breve título para o reporte.")
    descricao = models.TextField(help_text="Descreva detalhadamente o motivo do reporte.")
    imagem_evidencia = models.ImageField(upload_to='reportes_evidencias/', null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    notas_admin = models.TextField(blank=True, null=True, help_text="Notas internas do administrador sobre este reporte.")
    data_ultima_atualizacao_admin = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reporte #{self.id} - {self.titulo} (Status: {self.get_status_display()})"

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"