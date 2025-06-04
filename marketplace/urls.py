# marketplace/urls.py
from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'marketplace'

urlpatterns = [
    # Index URL
    path('', views.landing_page, name='landing_page'),

    # Comprador URLs
    path('comprador/login/', views.comprador_login, name='comprador_login'),
    path('comprador/cadastro/', views.comprador_cadastro, name='comprador_cadastro'),
    path('comprador/home/', views.home_comprador, name='pagina_inicial_comprador'),
    path('comprador/logout/', views.comprador_logout, name='comprador_logout'),
    path('comprador/produto/<int:produto_id>/', views.detalhes_produto, name='detalhes_produto'),
    path('comprador/busca/', views.pagina_busca_produto, name='pagina_busca_produto'),
    path('comprador/perfil/', views.comprador_perfil, name='comprador_perfil'),
    path('comprador/reportar-problema/', views.comprador_criar_reporte, name='comprador_criar_reporte'), # NEW URL for reporting

    # Lista de Desejos URLs
    path('comprador/lista-desejos/', views.lista_desejos, name='lista_desejos'),
    path('comprador/desejos/adicionar/<int:produto_id>/', views.adicionar_aos_desejos, name='adicionar_aos_desejos'),
    path('comprador/desejos/remover/<int:produto_id>/', views.remover_dos_desejos, name='remover_dos_desejos'),

    # Password Reset URLs (Comprador)
    path('comprador/esqueceu-senha/',
         auth_views.PasswordResetView.as_view(
             template_name='comprador/esquece_senha.html',
             email_template_name='comprador/esquece_senha_email_corpo.html',
             subject_template_name='comprador/esquece_senha_email_assunto.txt',
             success_url=reverse_lazy('marketplace:password_reset_done'),
             extra_email_context={'app_name': app_name}
         ),
         name='password_reset_request'),
    path('comprador/esqueceu-senha/email-enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='comprador/esquece_senha_email_enviado.html'
         ),
         name='password_reset_done'),
    path('comprador/resetar-senha/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='comprador/esquece_senha_nova_senha_form.html',
             success_url=reverse_lazy('marketplace:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('comprador/resetar-senha/concluido/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='comprador/esquece_senha_completo.html'
         ),
         name='password_reset_complete'),

    # Pedidos do Comprador
    path('comprador/pedidos/', views.comprador_pedidos, name='comprador_pedidos'),
    path('comprador/pedidos/fazer_pedido/<int:produto_id>/', views.fazer_pedido, name='fazer_pedido'),
    path('comprador/produto/<int:produto_id>/avaliar/', views.avaliar_produto, name='avaliar_produto'),

    # Vendedor URLs
    path('vendedor/login/', views.vendedor_login, name='vendedor_login'),
    path('vendedor/cadastro/', views.vendedor_cadastro, name='vendedor_cadastro'),
    path('vendedor/logout/', views.vendedor_logout, name='vendedor_logout'),
    path('vendedor/dashboard/', views.vendedor_dashboard, name='vendedor_dashboard'),
    path('vendedor/produtos/', views.vendedor_produtos, name='vendedor_produtos'),
    path('vendedor/produtos/adicionar/', views.vendedor_adicionar_produto, name='vendedor_adicionar_produto'),
    path('vendedor/produtos/editar/<int:produto_id>/', views.vendedor_editar_produto, name='vendedor_editar_produto'),
    path('vendedor/produtos/excluir/<int:produto_id>/', views.vendedor_excluir_produto, name='vendedor_excluir_produto'),
    path('vendedor/pedidos/', views.vendedor_orders, name='vendedor_pedidos'),
    path('vendedor/estoque/', views.vendedor_inventory, name='vendedor_estoque'),
    path('vendedor/avaliacoes/', views.vendedor_reviews, name='vendedor_avaliacoes'),
    path('vendedor/avaliacoes/responder/<int:avaliacao_id>/', views.vendedor_responder_avaliacao, name='vendedor_responder_avaliacao'),
    path('vendedor/relatorios/', views.vendedor_reports, name='vendedor_relatorios'),
    path('vendedor/pedidos/atualizar_status/<int:pedido_id>/', views.vendedor_update_order_status, name='vendedor_update_order_status'),
    path('vendedor/perfil/', views.vendedor_perfil, name='vendedor_perfil'),
    path('vendedor/reportar-problema/', views.vendedor_criar_reporte, name='vendedor_criar_reporte'), # NEW URL for reporting

    # Administrador URLs
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/anuncios/', views.admin_anuncios, name='admin_anuncios'),
    path('admin/anuncios/gerenciar/<int:produto_id>/', views.admin_gerenciar_anuncio, name='admin_gerenciar_anuncio'),
    path('admin/anuncios/excluir/<int:produto_id>/', views.admin_excluir_anuncio, name='admin_excluir_anuncio'),
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/usuarios/gerenciar/<int:user_id>/', views.admin_gerenciar_usuario, name='admin_gerenciar_usuario'),
    path('admin/usuarios/excluir/<int:user_id>/', views.admin_excluir_usuario, name='admin_excluir_usuario'),
    path('admin/reportes/', views.admin_reportes, name='admin_reportes'),
    path('admin/reportes/gerenciar/<int:reporte_id>/', views.admin_gerenciar_reporte, name='admin_gerenciar_reporte'),
    path('admin/reportes/arquivados/', views.admin_reportes_arquivados, name='admin_reportes_arquivados'),
    path('admin/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin/pedidos/gerenciar/<int:pedido_id>/', views.admin_gerenciar_pedido, name='admin_gerenciar_pedido'),
    path('admin/pedidos/finalizados/', views.admin_pedidos_finalizados, name='admin_pedidos_finalizados'),
]