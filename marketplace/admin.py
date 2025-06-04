# marketplace/admin.py
from django.contrib import admin
from .models import Produto, Pedido, Avaliacao, PerfilComprador, PerfilVendedor

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'vendedor', 'preco', 'estoque', 'criado_em')
    list_filter = ('vendedor', 'criado_em')
    search_fields = ('nome', 'descricao', 'vendedor__username')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'cliente', 'vendedor', 'quantidade', 'status', 'data_pedido')
    list_filter = ('status', 'data_pedido', 'vendedor', 'cliente')
    search_fields = ('produto__nome', 'cliente__username', 'vendedor__username')

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'cliente', 'nota', 'data_avaliacao')
    list_filter = ('nota', 'data_avaliacao', 'cliente')
    search_fields = ('produto__nome', 'cliente__username', 'comentario')

@admin.register(PerfilComprador)
class PerfilCompradorAdmin(admin.ModelAdmin):
    list_display = ('user', 'idade', 'cpf', 'curso', 'ra')
    search_fields = ('user__username', 'cpf', 'ra')

@admin.register(PerfilVendedor)
class PerfilVendedorAdmin(admin.ModelAdmin):
    list_display = ('user', 'idade', 'cpf', 'curso', 'ra')
    search_fields = ('user__username', 'cpf', 'ra')

