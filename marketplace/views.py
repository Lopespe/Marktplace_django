# marketplace/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator # Import Paginator
from .models import (
    Produto, Pedido, Avaliacao, PerfilComprador, PerfilVendedor,
    RespostaVendedorAvaliacao, Category # Import Category
)
from .forms import (
    FormCadastroComprador, FormCadastroVendedor,
    UserAdminEditForm, UserBuyerProfileEditForm, UserSellerProfileEditForm, # Updated and new User forms
    PerfilCompradorEditForm, PerfilVendedorEditForm,
    ProdutoForm, AvaliacaoForm, RespostaVendedorAvaliacaoForm,
)

from django.db.models import Sum, Count, Avg, F # F para referenciar campos do modelo em anotações
from django.urls import reverse_lazy
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q # Import Q for complex lookups

# Imports para o gráfico do admin_dashboard e vendedor_reports
from django.utils import timezone
import calendar

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View
from django.db import transaction
from django.contrib import messages

from .forms import UserSellerProfileEditForm, PerfilVendedorEditForm
from .models import PerfilVendedor

# --- FUNÇÕES DE TESTE DE PAPEL ---
def is_admin(user):
    return user.is_authenticated and user.is_staff

def is_comprador(user):
    return user.is_authenticated and user.groups.filter(name='Compradores').exists() and not user.is_staff

def is_vendedor(user):
    return user.is_authenticated and user.groups.filter(name='Vendedores').exists() and not user.is_staff

# --- VIEWS PÚBLICAS / INDEX ---
def landing_page(request):
    return render(request, 'comprador/landing_page.html')

# --- VIEWS DO ADMINISTRADOR ---
@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_dashboard(request):
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    recent_products = Produto.objects.all().order_by('-criado_em')[:5]
    try:
        compradores_group = Group.objects.get(name='Compradores')
        total_compradores = compradores_group.user_set.count()
    except Group.DoesNotExist:
        total_compradores = 0
    try:
        vendedores_group = Group.objects.get(name='Vendedores')
        total_vendedores = vendedores_group.user_set.count()
    except Group.DoesNotExist:
        total_vendedores = 0

    chart_labels = []
    chart_data = []
    today = timezone.now().date()
    meses_pt_abbr = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        month_name = meses_pt_abbr[month]
        chart_labels.append(f"{month_name}/{str(year)[-2:]}")
        registrations_in_month = User.objects.filter(date_joined__year=year, date_joined__month=month).count()
        chart_data.append(registrations_in_month)

    context = {
        'recent_users': recent_users, 'recent_products': recent_products,
        'total_compradores': total_compradores, 'total_vendedores': total_vendedores,
        'chart_labels': chart_labels, 'chart_data': chart_data,
    }
    return render(request, 'admin/dashboard.html', context)

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('marketplace:admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('marketplace:admin_dashboard')
        messages.error(request, 'Credenciais inválidas ou sem permissão de administrador.')
    return render(request, 'admin/login.html')

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_logout(request):
    logout(request)
    messages.info(request, "Você saiu da área administrativa.")
    return redirect('marketplace:admin_login')

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_anuncios(request):
    anuncios = Produto.objects.all().order_by('-criado_em')
    context = {'anuncios': anuncios}
    return render(request, 'admin/anuncios.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_gerenciar_anuncio(request, produto_id):
    anuncio = get_object_or_404(Produto, pk=produto_id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, f'Anúncio "{anuncio.nome}" atualizado com sucesso!')
            return redirect('marketplace:admin_anuncios')
        else:
            messages.error(request, 'Erro ao atualizar o anúncio. Verifique os campos.')
    else:
        form = ProdutoForm(instance=anuncio)
    context = {'anuncio': anuncio, 'form': form}
    return render(request, 'admin/gerenciar_anuncio.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_excluir_anuncio(request, produto_id):
    anuncio = get_object_or_404(Produto, pk=produto_id)
    if request.method == 'POST':
        try:
            nome_anuncio = anuncio.nome
            anuncio.delete()
            messages.success(request, f'Anúncio "{nome_anuncio}" excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir o anúncio: {e}')
        return redirect('marketplace:admin_anuncios')
    context = {'anuncio_a_excluir': anuncio}
    return render(request, 'admin/confirmar_exclusao_anuncio.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_usuarios(request):
    usuarios = User.objects.all().order_by('username')
    context = {'usuarios': usuarios}
    return render(request, 'admin/usuarios.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_gerenciar_usuario(request, user_id):
    usuario_a_gerenciar = get_object_or_404(User, pk=user_id)
    perfil_comprador = PerfilComprador.objects.filter(user=usuario_a_gerenciar).first()
    perfil_vendedor = PerfilVendedor.objects.filter(user=usuario_a_gerenciar).first()
    if request.method == 'POST':
        user_form = UserAdminEditForm(request.POST, instance=usuario_a_gerenciar)
        perfil_comprador_form = None
        perfil_vendedor_form = None
        forms_valid = user_form.is_valid()
        if perfil_comprador:
            perfil_comprador_form = PerfilCompradorEditForm(request.POST, instance=perfil_comprador, prefix="comprador")
            forms_valid = forms_valid and perfil_comprador_form.is_valid()
        if perfil_vendedor:
            perfil_vendedor_form = PerfilVendedorEditForm(request.POST, instance=perfil_vendedor, prefix="vendedor")
            forms_valid = forms_valid and perfil_vendedor_form.is_valid()
        if forms_valid:
            user_form.save()
            if perfil_comprador_form: perfil_comprador_form.save()
            if perfil_vendedor_form: perfil_vendedor_form.save()
            messages.success(request, f'Usuário {usuario_a_gerenciar.username} atualizado com sucesso!')
            return redirect('marketplace:admin_usuarios')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        user_form = UserAdminEditForm(instance=usuario_a_gerenciar)
        perfil_comprador_form = PerfilCompradorEditForm(instance=perfil_comprador, prefix="comprador") if perfil_comprador else None
        perfil_vendedor_form = PerfilVendedorEditForm(instance=perfil_vendedor, prefix="vendedor") if perfil_vendedor else None
    context = {
        'usuario_a_gerenciar': usuario_a_gerenciar, 'user_form': user_form,
        'perfil_comprador_form': perfil_comprador_form, 'perfil_vendedor_form': perfil_vendedor_form,
    }
    return render(request, 'admin/gerenciar_usuario.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_excluir_usuario(request, user_id):
    usuario_a_excluir = get_object_or_404(User, pk=user_id)
    if usuario_a_excluir == request.user:
        messages.error(request, "Você não pode excluir sua própria conta de administrador por aqui.")
        return redirect('marketplace:admin_usuarios')
    if request.method == 'POST':
        try:
            nome_usuario = usuario_a_excluir.username
            usuario_a_excluir.delete()
            messages.success(request, f'Usuário {nome_usuario} excluído com sucesso.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir usuário: {e}')
        return redirect('marketplace:admin_usuarios')
    context = {'usuario_a_excluir': usuario_a_excluir}
    return render(request, 'admin/confirmar_exclusao_usuario.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_pedidos(request):
    lista_pedidos = Pedido.objects.all().order_by('-data_pedido')
    context = {'pedidos': lista_pedidos}
    return render(request, 'admin/pedidos.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_gerenciar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    status_choices = Pedido._meta.get_field('status').choices
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in [choice[0] for choice in status_choices]:
            pedido.status = novo_status
            pedido.save()
            messages.success(request, f"Status do pedido #{pedido.id} atualizado para '{pedido.get_status_display()}'.")
            return redirect('marketplace:admin_gerenciar_pedido', pedido_id=pedido.id)
        else:
            messages.error(request, "Status inválido selecionado.")
    context = {'pedido': pedido, 'status_choices': status_choices}
    return render(request, 'admin/gerenciar_pedido.html', context)

@login_required(login_url=reverse_lazy('marketplace:admin_login'))
@user_passes_test(is_admin, login_url=reverse_lazy('marketplace:admin_login'))
def admin_pedidos_finalizados(request):
    pedidos_finalizados = Pedido.objects.filter(status='entregue').order_by('-data_pedido')
    context = {'pedidos_finalizados': pedidos_finalizados}
    return render(request, 'admin/pedidos_finalizados.html', context)


# --- VIEWS DO COMPRADOR ---
def comprador_login(request):
    # If the user is already authenticated, check if they are a buyer.
    # If they are, redirect to buyer home. If not, log them out and redirect to landing or login.
    if request.user.is_authenticated:
        if is_comprador(request.user):
            return redirect('marketplace:pagina_inicial_comprador')
        else:
            messages.info(request, 'Você já está logado, mas não como comprador. Faça logout para acessar a área de comprador ou utilize o login adequado.')
            logout(request) # Log out current user if not a buyer
            return redirect('marketplace:landing_page') # Redirect to landing page to clear state

    if request.method == 'POST':
        email = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            if is_comprador(user):
                login(request, user)
                return redirect('marketplace:pagina_inicial_comprador')
            elif is_admin(user) or is_vendedor(user):
                messages.error(request, 'Conta de vendedor/administrador. Por favor, utilize o login apropriado para sua função.')
                return render(request, 'comprador/login.html', {}) # Always pass a context
            else: # Authenticated user but not in any specific role (neither buyer, seller, nor admin group)
                messages.error(request, 'Sua conta não possui permissões de comprador. Por favor, entre em contato com o suporte.')
                return render(request, 'comprador/login.html', {}) # Always pass a context
        else: # Invalid credentials
            messages.error(request, 'Email ou senha inválidos.')
            return render(request, 'comprador/login.html', {}) # Always pass a context
    
    # For GET requests (or if user was logged out and redirected back here)
    return render(request, 'comprador/login.html', {}) # Always pass a context, even if empty

def comprador_cadastro(request):
    if request.user.is_authenticated: # If any user is logged in, redirect them
        return redirect('marketplace:pagina_inicial_comprador') # Assume redirect to buyer home or appropriate dashboard
    
    if request.method == 'POST':
        form = FormCadastroComprador(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=cd['email'], # Usando email como username
                    email=cd['email'],
                    password=cd['senha'],
                    first_name=cd['nome']
                )
                PerfilComprador.objects.create(
                    user=user,
                    idade=cd['idade'],
                    cpf=cd['cpf'],
                    curso=cd['curso'],
                    ra=cd['ra']
                )
                grupo_compradores, _ = Group.objects.get_or_create(name='Compradores')
                user.groups.add(grupo_compradores)

                login(request, user)
                messages.success(request, 'Cadastro realizado com sucesso! Você já está logado.')
                return redirect('marketplace:pagina_inicial_comprador')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro inesperado durante o cadastro: {e}')
                # Re-render the form with errors
                return render(request, 'comprador/cadastro.html', {'form': form})
        else:
            # Collect and display form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
            return render(request, 'comprador/cadastro.html', {'form': form}) # Render cadastro template again with errors
    else:
        form = FormCadastroComprador()
    return render(request, 'comprador/cadastro.html', {'form': form})

@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def home_comprador(request):
    produtos_disponiveis = Produto.objects.filter(estoque__gt=0).order_by('-criado_em')
    
    search_query = request.GET.get('q_search', '').strip()

    if search_query:
        produtos_disponiveis = produtos_disponiveis.filter(
            Q(nome__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(vendedor__first_name__icontains=search_query) |
            Q(vendedor__username__icontains=search_query)
        ).distinct()

    # Pagination
    paginator = Paginator(produtos_disponiveis, 9) # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtém o perfil do comprador logado
    perfil_comprador = get_object_or_404(PerfilComprador, user=request.user)
    # Obtém os IDs dos produtos na lista de desejos do comprador
    desejos_ids = perfil_comprador.desejos.values_list('id', flat=True)

    # Adiciona o status is_favorited a cada produto na página atual
    for produto in page_obj: # Iterate over page_obj, not all products
        produto.is_favorited = produto.id in desejos_ids

    context = {
        'nome_usuario': request.user.first_name or request.user.username,
        'page_obj': page_obj, # Pass page_obj instead of product_list
        # Removed filter_categorias as requested
        'search_query': search_query,
    }
    return render(request, 'comprador/home_comprador.html', context)


@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def pagina_busca_produto(request):
    produtos = Produto.objects.filter(estoque__gt=0).order_by('-criado_em')

    search_query = request.GET.get('q_search', '').strip()
    selected_category_id = request.GET.get('categoria') 

    filter_categories = Category.objects.all()

    if selected_category_id and selected_category_id != 'todos':
        try:
            selected_category_obj = Category.objects.get(id=selected_category_id)
            produtos = produtos.filter(category=selected_category_obj)
        except Category.DoesNotExist:
            messages.error(request, "Categoria inválida.")
            selected_category_id = None 

    if search_query:
        produtos = produtos.filter(
            Q(nome__icontains=search_query) |
            Q(descricao__icontains=search_query) |
            Q(vendedor__first_name__icontains=search_query) |
            Q(vendedor__username__icontains=search_query)
        ).distinct()

    # Pagination
    paginator = Paginator(produtos, 9) # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtém o perfil do comprador logado
    perfil_comprador = get_object_or_404(PerfilComprador, user=request.user)
    # Obtém os IDs dos produtos na lista de desejos do comprador
    desejos_ids = perfil_comprador.desejos.values_list('id', flat=True)

    # Adiciona o status is_favorited a cada produto na página atual
    for produto in page_obj: # Iterate over page_obj, not all products
        produto.is_favorited = produto.id in desejos_ids

    context = {
        'page_obj': page_obj, # Pass page_obj instead of product_list
        'search_query': search_query,
        'selected_category_id': selected_category_id,
    }
    return render(request, 'comprador/pagina_busca_produto.html', context)


@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def detalhes_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    avaliacoes = Avaliacao.objects.filter(produto=produto).select_related('cliente', 'resposta_do_vendedor').order_by('-data_avaliacao')
    
    # Verifica se o comprador já avaliou este produto
    user_has_reviewed = Avaliacao.objects.filter(produto=produto, cliente=request.user).exists()
    avaliacao_form = AvaliacaoForm() # Formulário para nova avaliação

    # Verifica se o produto está na lista de desejos do comprador
    perfil_comprador = get_object_or_404(PerfilComprador, user=request.user)
    is_favorited = produto in perfil_comprador.desejos.all()

    context = {
        'produto': produto,
        'avaliacoes': avaliacoes,
        'avaliacao_form': avaliacao_form,
        'user_has_reviewed': user_has_reviewed,
        'is_favorited': is_favorited,
    }
    return render(request, 'comprador/detalhes_produto.html', context)

@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def avaliar_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    
    # Verifica se o comprador já fez um pedido para este produto e se o pedido foi entregue.
    # Isso é para garantir que apenas compradores que realmente compraram e receberam o produto possam avaliá-lo.
    has_purchased_and_delivered = Pedido.objects.filter(
        cliente=request.user, 
        produto=produto, 
        status='entregue'
    ).exists()

    if not has_purchased_and_delivered:
        messages.error(request, "Você só pode avaliar produtos que comprou e que foram entregues.")
        return redirect('marketplace:detalhes_produto', produto_id=produto.id)

    # Impede múltiplas avaliações do mesmo usuário para o mesmo produto
    if Avaliacao.objects.filter(produto=produto, cliente=request.user).exists():
        messages.warning(request, "Você já avaliou este produto.")
        return redirect('marketplace:detalhes_produto', produto_id=produto.id)

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.produto = produto
            avaliacao.cliente = request.user
            avaliacao.save()
            messages.success(request, 'Sua avaliação foi enviada com sucesso!')
            return redirect('marketplace:detalhes_produto', produto_id=produto.id)
        else:
            messages.error(request, 'Erro ao enviar avaliação. Verifique os campos.')
            # To re-render the details page with errors, you need to pass product context
            return render(request, 'comprador/detalhes_produto.html', {
                'produto': produto,
                'avaliacoes': Avaliacao.objects.filter(produto=produto).select_related('cliente', 'resposta_do_vendedor').order_by('-data_avaliacao'),
                'avaliacao_form': form,
                'user_has_reviewed': False, # Still False for this submission
                'is_favorited': (produto in get_object_or_404(PerfilComprador, user=request.user).desejos.all())
            })
    
    # For GET requests, redirect to the product details page, as the review is submitted from there.
    return redirect('marketplace:detalhes_produto', produto_id=produto.id)


@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def fazer_pedido(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if request.method == 'POST':
        try:
            quantidade = int(request.POST.get('quantidade', 1))
            if quantidade <= 0:
                messages.error(request, "A quantidade deve ser um número positivo.")
                return redirect('marketplace:detalhes_produto', produto_id=produto.id)

            if produto.estoque == 0:
                messages.error(request, f"O produto '{produto.nome}' está esgotado.")
                return redirect('marketplace:detalhes_produto', produto_id=produto.id)

            if produto.estoque < quantidade:
                messages.error(request, f"Estoque insuficiente para {produto.nome}. Apenas {produto.estoque} unidade(s) disponível(eis).")
                return redirect('marketplace:detalhes_produto', produto_id=produto.id)
            
            # Simulate buyer balance check (uncomment and implement if you add balance field)
            # if request.user.perfil_comprador.balance < (produto.preco * quantidade):
            #    messages.error(request, "Saldo insuficiente para concluir o pedido.")
            #    return redirect('marketplace:detalhes_produto', produto_id=produto.id)

            # Cria o pedido
            pedido = Pedido.objects.create(
                produto=produto,
                cliente=request.user,
                vendedor=produto.vendedor, # O vendedor é o dono do produto
                quantidade=quantidade,
                status='pendente' # Define o status inicial como pendente
            )
            
            # Diminui o estoque do produto
            produto.estoque -= quantidade
            produto.save()

            messages.success(request, f"Pedido de {quantidade}x {produto.nome} realizado com sucesso! Aguarde a confirmação do vendedor.")
            return redirect('marketplace:comprador_pedidos') # Redireciona para a página de pedidos do comprador
        except ValueError:
            messages.error(request, "Quantidade inválida.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao processar o pedido: {e}")
    
    # For GET requests or if the POST fails, redirect to the product details page.
    return redirect('marketplace:detalhes_produto', produto_id=produto.id)

@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def comprador_pedidos(request):
    pedidos_do_comprador = Pedido.objects.filter(cliente=request.user).order_by('-data_pedido')

    # For each order, check if the associated product has already been reviewed by the user
    for pedido in pedidos_do_comprador:
        pedido.has_been_reviewed_by_user = Avaliacao.objects.filter(
            produto=pedido.produto,
            cliente=request.user
        ).exists()

    context = {
        'pedidos': pedidos_do_comprador
    }
    return render(request, 'comprador/pedidos.html', context)

@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def comprador_perfil(request):
    # This view allows the buyer to view and edit their profile details.
    perfil = get_object_or_404(PerfilComprador, user=request.user)
    
    if request.method == 'POST':
        user_form = UserBuyerProfileEditForm(request.POST, instance=request.user)
        perfil_form = PerfilCompradorEditForm(request.POST, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('marketplace:comprador_perfil')
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos.')
    else:
        user_form = UserBuyerProfileEditForm(instance=request.user)
        perfil_form = PerfilCompradorEditForm(instance=perfil)
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'comprador/perfil.html', context)

# --- VIEWS PARA LISTA DE DESEJOS ---
@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def adicionar_aos_desejos(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    perfil_comprador = get_object_or_404(PerfilComprador, user=request.user)

    if produto not in perfil_comprador.desejos.all():
        perfil_comprador.desejos.add(produto)
        messages.success(request, f'"{produto.nome}" adicionado à sua lista de desejos!')
    else:
        messages.info(request, f'"{produto.nome}" já está na sua lista de desejos.')
    
    return redirect(request.META.get('HTTP_REFERER', reverse_lazy('marketplace:pagina_inicial_comprador')))

@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def remover_dos_desejos(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    perfil_comprador = get_object_or_404(PerfilComprador, user=request.user)

    if produto in perfil_comprador.desejos.all():
        perfil_comprador.desejos.remove(produto)
        messages.success(request, f'"{produto.nome}" removido da sua lista de desejos.')
    else:
        messages.info(request, f'"{produto.nome}" não estava na sua lista de desejos.')

    return redirect(request.META.get('HTTP_REFERER', reverse_lazy('marketplace:lista_desejos')))

@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def lista_desejos(request):
    perfil_comprador = get_object_or_404(PerfilComprador, user=request.user)
    produtos_favoritados_list = perfil_comprador.desejos.all()

    for produto in produtos_favoritados_list:
        produto.is_favorited = True

    context = {
        'nome_usuario': request.user.first_name or request.user.username,
        'produtos_favoritados': produtos_favoritados_list,
    }
    return render(request, 'comprador/lista_desejos.html', context)


@login_required
@user_passes_test(is_comprador, login_url=reverse_lazy('marketplace:comprador_login'))
def comprador_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('marketplace:landing_page')

# --- VIEWS DO VENDEDOR ---
class EditarPerfilVendedorView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'vendedor/editar_perfil_vendedor.html'

    def test_func(self):
        # Garante que o usuário esteja logado E que ele tenha um perfil de vendedor.
        if not self.request.user.is_authenticated:
            return False
        try:
            # Tenta acessar o perfil de vendedor usando o related_name CORRETO.
            self.request.user.perfil_vendedor # CORRIGIDO: de perfilvendedor para perfil_vendedor
            return True
        except PerfilVendedor.DoesNotExist:
            return False

    def get(self, request, *args, **kwargs):
        user_form = UserSellerProfileEditForm(instance=request.user)
        try:
            # Acessa o perfil do vendedor usando o related_name CORRETO.
            perfil_vendedor = request.user.perfil_vendedor # CORRIGIDO: de perfilvendedor para perfil_vendedor
            perfil_form = PerfilVendedorEditForm(instance=perfil_vendedor)
        except PerfilVendedor.DoesNotExist:
            # Se por algum motivo o perfil não existir, cria um novo formulário de perfil vazio.
            # Embora test_func deva impedir isso, é uma segurança.
            perfil_form = PerfilVendedorEditForm()

        context = {
            'user_form': user_form,
            'perfil_form': perfil_form
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserSellerProfileEditForm(request.POST, instance=request.user)
        try:
            # Acessa o perfil do vendedor usando o related_name CORRETO.
            perfil_vendedor = request.user.perfil_vendedor # CORRIGIDO: de perfilvendedor para perfil_vendedor
            perfil_form = PerfilVendedorEditForm(request.POST, instance=perfil_vendedor)
        except PerfilVendedor.DoesNotExist:
            # Se o perfil não existir durante o POST (o que é improvável se test_func funcionar),
            # cria uma nova instância de PerfilVendedor.
            perfil_form = PerfilVendedorEditForm(request.POST)

        if user_form.is_valid() and perfil_form.is_valid():
            with transaction.atomic():
                user_form.save()
                perfil = perfil_form.save(commit=False)
                perfil.user = request.user
                perfil.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            # Assumindo que 'marketplace:perfil_vendedor' existe e leva à visualização do perfil.
            return redirect('marketplace:vendedor_dashboard') # Redireciona para o dashboard do vendedor ou para uma página de perfil
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Por favor, verifique os dados informados.')
            context = {
                'user_form': user_form,
                'perfil_form': perfil_form
            }
            return render(request, self.template_name, context)

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_dashboard(request):
    num_produtos_ativos = Produto.objects.filter(vendedor=request.user, estoque__gt=0).count()
    num_pedidos_pendentes = Pedido.objects.filter(vendedor=request.user, status__in=['pendente', 'preparando']).count()
    
    pedidos_entregues_vendedor = Pedido.objects.filter(vendedor=request.user, status='entregue')
    total_vendas_mes_atual_valor = pedidos_entregues_vendedor.filter(
        data_pedido__year=timezone.now().year,
        data_pedido__month=timezone.now().month
    ).annotate(
        valor_item_total=F('produto__preco') * F('quantidade')
    ).aggregate(total=Sum('valor_item_total'))['total'] or 0.00

    produtos_do_vendedor = Produto.objects.filter(vendedor=request.user)
    media_avaliacoes = Avaliacao.objects.filter(produto__in=produtos_do_vendedor).aggregate(Avg('nota'))['nota__avg']
    media_avaliacoes_formatada = f"{media_avaliacoes:.1f}" if media_avaliacoes else "N/A"

    recent_avaliacoes = Avaliacao.objects.filter(produto__in=produtos_do_vendedor).select_related('cliente', 'produto', 'resposta_do_vendedor').order_by('-data_avaliacao')[:3]

    vendedor_chart_labels = []
    vendedor_chart_data = []
    today = timezone.now().date()
    meses_pt_abbr = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        
        month_name = meses_pt_abbr[month]
        vendedor_chart_labels.append(f"{month_name}/{str(year)[-2:]}")

        vendas_no_mes = pedidos_entregues_vendedor.filter(
            data_pedido__year=year,
            data_pedido__month=month
        ).annotate(
            valor_total_item=F('produto__preco') * F('quantidade')
        ).aggregate(total_mes=Sum('valor_total_item'))['total_mes'] or 0.00
        vendedor_chart_data.append(float(vendas_no_mes))

    context = {
        'num_produtos_ativos': num_produtos_ativos,
        'num_pedidos_pendentes': num_pedidos_pendentes,
        'total_vendas_mes_atual': total_vendas_mes_atual_valor,
        'media_avaliacoes_produtos': media_avaliacoes_formatada,
        'recent_avaliacoes': recent_avaliacoes,
        'chart_labels': vendedor_chart_labels,
        'chart_data': vendedor_chart_data,
    }
    return render(request, 'vendedor/dashboard.html', context)

def vendedor_login(request):
    if request.user.is_authenticated and is_vendedor(request.user):
        return redirect('marketplace:vendedor_dashboard')
    if request.method == 'POST':
        form_data = request.POST
        email = form_data.get('username')
        senha = form_data.get('password')
        user = authenticate(request, username=email, password=senha)
        if user:
            if is_vendedor(user):
                login(request, user)
                return redirect('marketplace:vendedor_dashboard')
            elif is_admin(user):
                messages.error(request, 'Conta de administrador. Use o login de admin.')
            else:
                messages.error(request, 'Tipo de usuário incorreto para esta área.')
        else:
            messages.error(request, 'Email e/ou senha inválidos.')
    return render(request, 'vendedor/login.html')

def vendedor_cadastro(request):
    if request.user.is_authenticated: return redirect('marketplace:vendedor_dashboard')
    if request.method == 'POST':
        form = FormCadastroVendedor(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = User.objects.create_user(
                    username=cd['email'], email=cd['email'], password=cd['senha'],
                    first_name=cd['nome'], is_staff=False, is_superuser=False
                )
                PerfilVendedor.objects.create(
                    user=user, idade=cd['idade'], cpf=cd['cpf'],
                    curso=cd['curso'], ra=cd['ra']
                )
                grupo_vendedores, _ = Group.objects.get_or_create(name='Vendedores')
                user.groups.add(grupo_vendedores)
                login(request, user)
                messages.success(request, 'Cadastro de vendedor realizado com sucesso!')
                return redirect('marketplace:vendedor_dashboard')
            except Exception as e:
                messages.error(request, f'Ocorreu um erro durante o cadastro: {e}. Por favor, tente novamente.')
    else:
        form = FormCadastroVendedor()
    return render(request, 'vendedor/cadastro.html', {'form': form})

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_logout(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta de vendedor.")
    return redirect('marketplace:landing_page')

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_produtos(request):
    produtos = Produto.objects.filter(vendedor=request.user).order_by('-criado_em')
    return render(request, 'vendedor/produtos.html', {'produtos': produtos})

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_adicionar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.vendedor = request.user
            produto.save()
            messages.success(request, 'Produto adicionado com sucesso!')
            return redirect('marketplace:vendedor_produtos')
        else:
            messages.error(request, 'Erro ao adicionar o produto. Verifique os campos.')
    else:
        form = ProdutoForm()
    return render(request, 'vendedor/produto_form.html', {'form': form, 'acao': 'Adicionar'})

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, vendedor=request.user)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso.')
            return redirect('marketplace:vendedor_produtos')
        else: # Added else to render form with errors if invalid
            messages.error(request, 'Erro ao atualizar o produto. Verifique os campos.')
            return render(request, 'vendedor/produto_form.html', {'form': form, 'acao': 'Editar', 'produto': produto})
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'vendedor/produto_form.html', {'form': form, 'acao': 'Editar', 'produto': produto})

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_excluir_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, vendedor=request.user)
    if request.method == 'POST':
        nome_produto = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome_produto}" excluído com sucesso.')
        return redirect('marketplace:vendedor_produtos')
    return render(request, 'vendedor/confirmar_exclusao.html', {'produto': produto})

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_orders(request):
    pedidos_recebidos = Pedido.objects.filter(vendedor=request.user).select_related('produto', 'cliente').order_by('-data_pedido')
    context = {'pedidos': pedidos_recebidos} # Pass original queryset, template calculates total
    return render(request, 'vendedor/pedidos.html', context)

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_inventory(request):
    produtos = Produto.objects.filter(vendedor=request.user)
    if request.method == 'POST':
        for produto in produtos:
            novo_estoque_str = request.POST.get(f'estoque_{produto.id}')
            if novo_estoque_str is not None and novo_estoque_str.strip() != '':
                try:
                    novo_estoque = int(novo_estoque_str)
                    if novo_estoque >= 0:
                        produto.estoque = novo_estoque
                        produto.save(update_fields=['estoque'])
                    else:
                        messages.error(request, f'Estoque para "{produto.nome}" não pode ser negativo.')
                except ValueError:
                    messages.error(request, f'Valor de estoque inválido para "{produto.nome}". Use apenas números.')
            elif novo_estoque_str is not None and novo_estoque_str.strip() == '':
                 messages.warning(request, f'Nenhum valor fornecido para o estoque de "{produto.nome}". Não foi alterado.')
        messages.success(request, 'Estoque atualizado (onde aplicável).')
        return redirect('marketplace:vendedor_estoque')
    return render(request, 'vendedor/estoque.html', {'produtos': produtos})

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_reviews(request):
    produtos_do_vendedor = Produto.objects.filter(vendedor=request.user)
    avaliacoes = Avaliacao.objects.filter(produto__in=produtos_do_vendedor).select_related('cliente', 'produto', 'resposta_do_vendedor').order_by('-data_avaliacao')
    context = {'avaliacoes': avaliacoes}
    return render(request, 'vendedor/avaliacoes.html', context)

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_responder_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id, produto__vendedor=request.user)
    # Verifica se já existe uma resposta para não permitir múltiplas
    try:
        resposta_existente = RespostaVendedorAvaliacao.objects.get(avaliacao=avaliacao)
        form = RespostaVendedorAvaliacaoForm(request.POST or None, instance=resposta_existente) # Use request.POST or None
    except RespostaVendedorAvaliacao.DoesNotExist:
        resposta_existente = None
        form = RespostaVendedorAvaliacaoForm(request.POST or None) # Use request.POST or None

    if request.method == 'POST':
        if form.is_valid():
            resposta = form.save(commit=False)
            resposta.avaliacao = avaliacao
            resposta.vendedor = request.user
            resposta.save()
            if resposta_existente:
                messages.success(request, "Sua resposta foi atualizada.")
            else:
                messages.success(request, "Sua resposta foi enviada.")
            return redirect('marketplace:vendedor_avaliacoes')
        else:
            messages.error(request, "Erro ao salvar resposta. Verifique os campos.") # Added error message
            # Re-render the page with the form and errors
            context = {'form': form, 'avaliacao': avaliacao, 'resposta_existente': resposta_existente}
            return render(request, 'vendedor/responder_avaliacao.html', context)
    
    context = {'form': form, 'avaliacao': avaliacao, 'resposta_existente': resposta_existente}
    return render(request, 'vendedor/responder_avaliacao.html', context)

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_update_order_status(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, vendedor=request.user) # Ensure seller owns the order
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Pedido.STATUS_CHOICES]

        if new_status and new_status in valid_statuses:
            # Prevent changing status if it's already 'entregue' or 'cancelado' (terminal states)
            if pedido.status in ['entregue', 'cancelado']:
                messages.error(request, f"O pedido já está '{pedido.get_status_display()}' e não pode ser alterado.")
            else:
                pedido.status = new_status
                pedido.save()
                messages.success(request, f"Status do Pedido #{pedido.id} atualizado para '{pedido.get_status_display()}' com sucesso!")
        else:
            messages.error(request, "Status inválido fornecido.")
    else:
        messages.warning(request, "Método não permitido para esta operação.")
    
    return redirect('marketplace:vendedor_pedidos') # Redirect back to the orders list

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_perfil(request):
    perfil = get_object_or_404(PerfilVendedor, user=request.user)
    
    if request.method == 'POST':
        user_form = UserSellerProfileEditForm(request.POST, instance=request.user)
        perfil_form = PerfilVendedorEditForm(request.POST, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, 'Seu perfil de vendedor foi atualizado com sucesso!')
            return redirect('marketplace:vendedor_perfil')
        else:
            messages.error(request, 'Erro ao atualizar o perfil. Verifique os campos.')
    else:
        user_form = UserSellerProfileEditForm(instance=request.user)
        perfil_form = PerfilVendedorEditForm(instance=perfil)
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'nome_usuario': request.user.first_name or request.user.username,
    }
    return render(request, 'vendedor/perfil.html', context)

@login_required(login_url=reverse_lazy('marketplace:vendedor_login'))
@user_passes_test(is_vendedor, login_url=reverse_lazy('marketplace:vendedor_login'))
def vendedor_reports(request):
    pedidos_vendedor = Pedido.objects.filter(vendedor=request.user)
    pedidos_entregues = pedidos_vendedor.filter(status='entregue')

    total_vendas_valor = pedidos_entregues.annotate(
        valor_item_total=F('produto__preco') * F('quantidade')
    ).aggregate(total_vendas=Sum('valor_item_total'))['total_vendas'] or 0

    total_itens_vendidos = pedidos_entregues.aggregate(total_qtd=Sum('quantidade'))['total_qtd'] or 0
    total_pedidos_concluidos = pedidos_entregues.count()

    produtos_mais_vendidos = Produto.objects.filter(vendedor=request.user, pedido__status='entregue') \
                                       .annotate(total_vendido=Sum('pedido__quantidade')) \
                                       .filter(total_vendido__gt=0) \
                                       .order_by('-total_vendido')[:5]
    
    produtos_mais_avaliados = Produto.objects.filter(vendedor=request.user) \
                                       .annotate(num_avaliacoes=Count('avaliacoes'), media_nota=Avg('avaliacoes__nota')) \
                                       .filter(num_avaliacoes__gt=0) \
                                       .order_by('-num_avaliacoes', '-media_nota')[:5]

    produtos_mais_curtidos = [] # Implementar se houver um sistema de curtidas

    # Dados do gráfico de vendas por mês (últimos 6 meses)
    report_chart_labels = []
    report_chart_data = []
    today = timezone.now().date()
    meses_pt_abbr = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1
        
        month_name = meses_pt_abbr[month]
        report_chart_labels.append(f"{month_name}/{str(year)[-2:]}")

        vendas_no_mes = pedidos_entregues.filter(
            data_pedido__year=year,
            data_pedido__month=month
        ).annotate(
            valor_total_item=F('produto__preco') * F('quantidade')
        ).aggregate(total_mes=Sum('valor_total_item'))['total_mes'] or 0
        report_chart_data.append(float(vendas_no_mes))


    context = {
        'total_vendas_valor': total_vendas_valor,
        'total_itens_vendidos': total_itens_vendidos,
        'total_pedidos_concluidos': total_pedidos_concluidos,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'produtos_mais_avaliados': produtos_mais_avaliados,
        'produtos_mais_curtidos': produtos_mais_curtidos,
        'vendas_por_mes_labels': report_chart_labels,
        'vendas_por_mes_data': report_chart_data,
    }
    return render(request, 'vendedor/relatorios.html', context)