from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
import importlib
from decimal import Decimal

from marketplace.models import (
    Produto, PerfilComprador, PerfilVendedor, Category,
    Pedido, Avaliacao, RespostaVendedorAvaliacao,
)
from marketplace.forms import (
    FormCadastroComprador, FormCadastroVendedor,
    ProdutoForm, AvaliacaoForm,
    UserAdminEditForm, UserBuyerProfileEditForm,
    UserSellerProfileEditForm, PerfilCompradorEditForm,
    PerfilVendedorEditForm, RespostaVendedorAvaliacaoForm
)


class BaseTestCase(TestCase):
    """
    Base test class to set up common data for all tests.
    """
    def setUp(self):
        # Create groups
        self.group_compradores = Group.objects.create(name='Compradores')
        self.group_vendedores = Group.objects.create(name='Vendedores')

        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='admin123'
        )
        self.comprador_user = User.objects.create_user(
            username='comprador@test.com', email='comprador@test.com',
            password='comprador123'
        )
        self.comprador_user.groups.add(self.group_compradores)
        self.vendedor_user = User.objects.create_user(
            username='vendedor@test.com', email='vendedor@test.com',
            password='vendedor123'
        )
        self.vendedor_user.groups.add(self.group_vendedores)

        # Create profiles
        self.perfil_comprador = PerfilComprador.objects.create(user=self.comprador_user)
        self.perfil_vendedor = PerfilVendedor.objects.create(user=self.vendedor_user)

        # Create category and product
        self.categoria = Category.objects.create(name='Eletrônicos')
        self.produto = Produto.objects.create(
            vendedor=self.vendedor_user,
            nome='Notebook',
            descricao='Notebook potente',
            preco=4500.00,
            estoque=10,
            category=self.categoria
        )

        self.client = Client()


class ModelStrTests(TestCase):
    """
    Tests for the __str__ methods of models to ensure correct string representation.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='usuario1', email='user1@example.com', password='senha123')
        self.vendedor = User.objects.create_user(username='vendedor1', email='vendedor@example.com', password='senha123')
        self.comprador = User.objects.create_user(username='comprador1', email='comprador@example.com', password='senha123')

        self.categoria = Category.objects.create(name='Livros')
        self.perfil_comprador = PerfilComprador.objects.create(user=self.comprador)
        self.perfil_vendedor = PerfilVendedor.objects.create(user=self.vendedor)
        self.produto = Produto.objects.create(
            vendedor=self.vendedor,
            nome='Livro de Django',
            descricao='Um livro excelente',
            preco=99.90,
            estoque=5,
            category=self.categoria
        )
        self.pedido = Pedido.objects.create(
            vendedor=self.vendedor,
            cliente=self.comprador,
            produto=self.produto,
            quantidade=2
        )
        self.avaliacao = Avaliacao.objects.create(
            produto=self.produto,
            cliente=self.comprador,
            nota=4,
            comentario='Muito bom!'
        )
        self.resposta = RespostaVendedorAvaliacao.objects.create(
            avaliacao=self.avaliacao,
            vendedor=self.vendedor,
            texto='Obrigado pelo feedback!'
        )

    def test_categoria_str(self):
        self.assertEqual(str(self.categoria), 'Livros')

    def test_perfil_comprador_str(self):
        self.assertEqual(str(self.perfil_comprador), f"Perfil de {self.comprador.username}")

    def test_perfil_vendedor_str(self):
        self.assertEqual(str(self.perfil_vendedor), f"Perfil de Vendedor: {self.vendedor.username}")

    def test_produto_str(self):
        self.assertEqual(str(self.produto), f"{self.produto.nome} - {self.vendedor.username}")

    def test_pedido_str(self):
        self.assertEqual(str(self.pedido), f"Pedido #{self.pedido.pk} - {self.produto.nome} ({self.pedido.quantidade}) por {self.comprador.username}")

    def test_avaliacao_str(self):
        self.assertEqual(str(self.avaliacao), f"Avaliação de {self.comprador.username} para {self.produto.nome} (Nota: {self.avaliacao.nota})")

    def test_resposta_vendedor_avaliacao_str(self):
        self.assertEqual(str(self.resposta), f"Resposta de {self.vendedor.username} para avaliação #{self.avaliacao.id}")


class StaticMediaUrlIntegrationTests(TestCase):
    """
    Tests the integration of static and media URLs in Django settings.
    """
    @override_settings(DEBUG=True)
    def test_mysite_urls_includes_media_when_debug(self):
        # Force reload of mysite.urls to apply DEBUG=True
        import mysite.urls
        importlib.reload(mysite.urls)
        media_url = settings.MEDIA_URL.strip('/')
        found = any(
            hasattr(p.pattern, 'regex') and media_url in p.pattern.regex.pattern
            for p in mysite.urls.urlpatterns
        )
        self.assertTrue(
            found,
            f"MEDIA_URL ('{settings.MEDIA_URL}') não foi encontrado nas urlpatterns em DEBUG=True."
        )


class FormValidationTests(TestCase):
    """
    Comprehensive tests for form validations, including basic validity,
    password matching, and unique email constraints.
    """
    def setUp(self):
        self.category = Category.objects.create(name='Eletrônicos')
        self.existing_user = User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='123'
        )

    # FormCadastroComprador Tests
    def test_valid_comprador_form(self):
        form = FormCadastroComprador(data={
            'nome': 'João da Silva',
            'idade': 22,
            'cpf': '12345678901',
            'curso': 'Engenharia',
            'ra': '12345',
            'email': 'joao@example.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_comprador_form_senhas_diferentes(self):
        form = FormCadastroComprador(data={
            'nome': 'João da Silva',
            'idade': 22,
            'cpf': '12345678901',
            'curso': 'Engenharia',
            'ra': '12345',
            'email': 'joao@example.com',
            'senha': 'senha123',
            'confirmar_senha': 'outra123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirmar_senha', form.errors)
        self.assertIn('As senhas não coincidem', str(form.errors['confirmar_senha']))


    def test_comprador_form_email_ja_cadastrado(self):
        form = FormCadastroComprador(data={
            'nome': 'Usuário',
            'idade': 20,
            'cpf': '12345678900',
            'curso': 'Engenharia',
            'ra': '123456',
            'email': 'existing@example.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Este email já está cadastrado', str(form.errors['email']))

    # FormCadastroVendedor Tests
    def test_valid_vendedor_form(self):
        form = FormCadastroVendedor(data={
            'nome': 'Maria Vendedora',
            'idade': 30,
            'cpf': '98765432100',
            'curso': 'Administração',
            'ra': '54321',
            'email': 'maria@example.com',
            'senha': 'senha456',
            'confirmar_senha': 'senha456',
        })
        self.assertTrue(form.is_valid())

    def test_vendedor_form_senhas_diferentes(self):
        form = FormCadastroVendedor(data={
            'nome': 'Carlos Vendedor',
            'idade': 30,
            'cpf': '11122233344',
            'curso': 'Gestão',
            'ra': '998877',
            'email': 'carlos@example.com',
            'senha': 'senha123',
            'confirmar_senha': 'outra_senha',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirmar_senha', form.errors)
        self.assertIn('As senhas não coincidem', str(form.errors['confirmar_senha']))

    def test_vendedor_form_email_ja_cadastrado(self):
        form = FormCadastroVendedor(data={
            'nome': 'Vendedor',
            'idade': 22,
            'cpf': '98765432100',
            'curso': 'Administração',
            'ra': '654321',
            'email': 'existing@example.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Este email já está cadastrado', str(form.errors['email']))

    # ProdutoForm Tests
    def test_valid_produto_form(self):
        form = ProdutoForm(data={
            'nome': 'Fone de Ouvido',
            'descricao': 'Excelente som',
            'preco': 199.90,
            'estoque': 5,
            'category': self.category.id,
        })
        self.assertTrue(form.is_valid())

    # AvaliacaoForm Tests
    def test_valid_avaliacao_form(self):
        form = AvaliacaoForm(data={
            'nota': 5,
            'comentario': 'Muito bom!',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_avaliacao_form_nota_faltando(self):
        form = AvaliacaoForm(data={
            'comentario': 'Faltou nota.',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nota', form.errors)

    # User Buyer/Seller Profile Edit Form Tests
    def test_user_buyer_edit_form_email_ja_usado(self):
        User.objects.create_user(username='alguem', email='outro@example.com', password='123') # Create another user with an email
        form = UserBuyerProfileEditForm(instance=self.existing_user, data={
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'outro@example.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Este email já está em uso por outra conta.', str(form.errors['email']))

    def test_user_seller_edit_form_email_ja_usado(self):
        User.objects.create_user(username='alguem', email='outro@example.com', password='123') # Create another user with an email
        form = UserSellerProfileEditForm(instance=self.existing_user, data={
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'outro@example.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Este email já está em uso por outra conta.', str(form.errors['email']))


class ProfileEditFormTests(TestCase):
    """
    Tests for forms related to editing user profiles (Comprador and Vendedor)
    and vendor responses to evaluations.
    """
    def test_admin_edit_form(self):
        group = Group.objects.create(name="TestGroup")
        user = User.objects.create_user(username="adminform", email="adminform@test.com")
        form = UserAdminEditForm(instance=user, data={
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'novoemail@test.com',
            'is_active': True,
            'is_staff': False,
            'groups': [group.id],
        })
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertIn(group, instance.groups.all())

    def test_buyer_profile_edit_form(self):
        user = User.objects.create_user(username='compradoruser', email='comprador@test.com')
        form = UserBuyerProfileEditForm(instance=user, data={
            'first_name': 'João',
            'last_name': 'Silva',
            'email': 'joao@novo.com'
        })
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, 'joao@novo.com')

    def test_seller_profile_edit_form(self):
        user = User.objects.create_user(username='vendedoruser', email='vendedor@test.com')
        form = UserSellerProfileEditForm(instance=user, data={
            'first_name': 'Maria',
            'last_name': 'Vendedora',
            'email': 'maria@novo.com'
        })
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.username, 'maria@novo.com')

    def test_perfil_comprador_form(self):
        user = User.objects.create_user(username='comprador_edit', email='c@t.com')
        perfil = PerfilComprador.objects.create(user=user)
        form = PerfilCompradorEditForm(instance=perfil, data={
            'idade': 25,
            'cpf': '12345678900',
            'curso': 'Engenharia',
            'ra': '112233'
        })
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.curso, 'Engenharia')

    def test_perfil_vendedor_form(self):
        user = User.objects.create_user(username='vendedor_edit', email='v@t.com')
        perfil = PerfilVendedor.objects.create(user=user)
        form = PerfilVendedorEditForm(instance=perfil, data={
            'idade': 28,
            'cpf': '98765432100',
            'curso': 'Marketing',
            'ra': '445566'
        })
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.ra, '445566')

    def test_resposta_form(self):
        cliente = User.objects.create_user(username='cliente', email='cli@t.com')
        vendedor = User.objects.create_user(username='vendedor', email='vend@t.com')
        produto = Produto.objects.create(
            vendedor=vendedor, nome='Item', descricao='...', preco=10.00, estoque=2
        )
        avaliacao = Avaliacao.objects.create(produto=produto, cliente=cliente, nota=5)
        form = RespostaVendedorAvaliacaoForm(data={
            'texto': 'Obrigado!'
        })
        self.assertTrue(form.is_valid())


class ViewTests(BaseTestCase):
    """
    Tests for Django views, covering page access, authentication, and core functionalities.
    """
    def test_landing_page_view(self):
        response = self.client.get(reverse('marketplace:landing_page'))
        self.assertEqual(response.status_code, 200)

    def test_comprador_login_view_get(self):
        response = self.client.get(reverse('marketplace:comprador_login'))
        self.assertEqual(response.status_code, 200)

    def test_comprador_login_view_post(self):
        response = self.client.post(reverse('marketplace:comprador_login'), {
            'username': 'comprador@test.com',
            'password': 'comprador123'
        })
        self.assertRedirects(response, reverse('marketplace:pagina_inicial_comprador'))

    def test_comprador_home_requires_login(self):
        response = self.client.get(reverse('marketplace:pagina_inicial_comprador'))
        self.assertRedirects(response, '/comprador/login/?next=/comprador/home/')

    def test_comprador_home_authenticated(self):
        self.client.login(username='comprador@test.com', password='comprador123')
        response = self.client.get(reverse('marketplace:pagina_inicial_comprador'))
        self.assertEqual(response.status_code, 200)

    def test_detalhes_produto_view(self):
        self.client.login(username='comprador@test.com', password='comprador123')
        response = self.client.get(reverse('marketplace:detalhes_produto', args=[self.produto.id]))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_access(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('marketplace:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')

    def test_vendedor_dashboard_access(self):
        self.client.login(username='vendedor@test.com', password='vendedor123')
        response = self.client.get(reverse('marketplace:vendedor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_fazer_pedido(self):
        self.client.login(username='comprador@test.com', password='comprador123')
        response = self.client.post(reverse('marketplace:fazer_pedido', args=[self.produto.id]), {
            'quantidade': 1
        })
        self.assertRedirects(response, reverse('marketplace:comprador_pedidos'))
        self.assertEqual(Pedido.objects.count(), 1)

    def test_comprador_logout(self):
        self.client.login(username='comprador@test.com', password='comprador123')
        response = self.client.get(reverse('marketplace:comprador_logout'))
        self.assertRedirects(response, reverse('marketplace:landing_page'))

    def test_adicionar_remover_desejo(self):
        self.client.login(username='comprador@test.com', password='comprador123')
        self.client.get(reverse('marketplace:adicionar_aos_desejos', args=[self.produto.id]))
        self.assertIn(self.produto, self.perfil_comprador.desejos.all())
        self.client.get(reverse('marketplace:remover_dos_desejos', args=[self.produto.id]))
        self.assertNotIn(self.produto, self.perfil_comprador.desejos.all())

    # --- Testes para as Views de ADMIN ---

    def test_admin_dashboard_requires_staff(self):
        # Comprador não deve acessar
        self.client.login(username='comprador@test.com', password='comprador123')
        response = self.client.get(reverse('marketplace:admin_dashboard'))
        self.assertEqual(response.status_code, 403) # Forbidden
        # Vendedor não deve acessar
        self.client.login(username='vendedor@test.com', password='vendedor123')
        response = self.client.get(reverse('marketplace:admin_dashboard'))
        self.assertEqual(response.status_code, 403) # Forbidden
        # Usuário não logado deve ser redirecionado para o login do admin
        self.client.logout()
        response = self.client.get(reverse('marketplace:admin_dashboard'))
        self.assertRedirects(response, reverse('marketplace:admin_login') + '?next=/admin/')


class AdminViewTests(TestCase):
    def setUp(self):
        # 1. Criar um superuser para acessar o admin
        self.admin_user = User.objects.create_superuser(
            username='admin_test', email='admin_test@example.com', password='adminpassword'
        )
        self.client = Client()
        self.client.login(username='admin_test', password='adminpassword')

        # 2. Criar instâncias de modelos para testar as views de mudança (change views)
        self.category = Category.objects.create(name='AdminTestCategory')
        self.comprador_user = User.objects.create_user(username='comprador_admin_test', email='comprador_admin_test@example.com', password='testpassword')
        self.vendedor_user = User.objects.create_user(username='vendedor_admin_test', email='vendedor_admin_test@example.com', password='testpassword')
        
        self.perfil_comprador = PerfilComprador.objects.create(user=self.comprador_user, idade=25, cpf='11122233344', curso='Engenharia', ra='12345')
        self.perfil_vendedor = PerfilVendedor.objects.create(user=self.vendedor_user, idade=30, cpf='55566677788', curso='Gestao', ra='67890')
        
        self.produto = Produto.objects.create(
            vendedor=self.vendedor_user,
            nome='Produto Admin Teste',
            descricao='Descricao para teste de admin',
            preco=Decimal('100.00'), # Usar Decimal
            estoque=5,
            category=self.category
        )
        self.pedido = Pedido.objects.create(
            vendedor=self.vendedor_user,
            cliente=self.comprador_user,
            produto=self.produto,
            quantidade=1,
            status='pendente'
        )
        self.avaliacao = Avaliacao.objects.create(
            produto=self.produto,
            cliente=self.comprador_user,
            nota=5,
            comentario='Ótimo produto!'
        )
        self.resposta_avaliacao = RespostaVendedorAvaliacao.objects.create(
            avaliacao=self.avaliacao,
            vendedor=self.vendedor_user,
            texto='Obrigado pela avaliação!'
        )

    def _get_admin_url(self, model, view_name, obj_id=None):
        """Helper to get admin URL for a model."""
        info = (model._meta.app_label, model._meta.model_name)
        if obj_id:
            return reverse(f'admin:{info[0]}_{info[1]}_{view_name}', args=[obj_id])
        return reverse(f'admin:{info[0]}_{info[1]}_{view_name}')

    # Testes de Acesso Geral ao Admin
    def test_admin_dashboard_access(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administração do site") # Verifica se a página carregou o título padrão do admin

    # Testes para o modelo User
    def test_user_changelist_view(self):
        url = self._get_admin_url(User, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin_user.username)
        self.assertContains(response, self.comprador_user.username)
        self.assertContains(response, self.vendedor_user.username)

    def test_user_add_view_get(self):
        url = self._get_admin_url(User, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar usuário")

    def test_user_change_view_get(self):
        url = self._get_admin_url(User, 'change', obj_id=self.comprador_user.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.comprador_user.email)

    # Testes para o modelo Category
    def test_category_changelist_view(self):
        url = self._get_admin_url(Category, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)

    def test_category_add_view_get(self):
        url = self._get_admin_url(Category, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar categoria")

    def test_category_change_view_get(self):
        url = self._get_admin_url(Category, 'change', obj_id=self.category.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)

    # Testes para o modelo PerfilComprador
    def test_perfilcomprador_changelist_view(self):
        url = self._get_admin_url(PerfilComprador, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.perfil_comprador.user.username)

    def test_perfilcomprador_add_view_get(self):
        url = self._get_admin_url(PerfilComprador, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar perfil comprador")

    def test_perfilcomprador_change_view_get(self):
        url = self._get_admin_url(PerfilComprador, 'change', obj_id=self.perfil_comprador.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.perfil_comprador.idade)) # Convert to string as it appears in HTML

    # Testes para o modelo PerfilVendedor
    def test_perfilvendedor_changelist_view(self):
        url = self._get_admin_url(PerfilVendedor, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.perfil_vendedor.user.username)

    def test_perfilvendedor_add_view_get(self):
        url = self._get_admin_url(PerfilVendedor, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar perfil vendedor")

    def test_perfilvendedor_change_view_get(self):
        url = self._get_admin_url(PerfilVendedor, 'change', obj_id=self.perfil_vendedor.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.perfil_vendedor.idade))

    # Testes para o modelo Produto
    def test_produto_changelist_view(self):
        url = self._get_admin_url(Produto, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produto.nome)

    def test_produto_add_view_get(self):
        url = self._get_admin_url(Produto, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar produto")

    def test_produto_change_view_get(self):
        url = self._get_admin_url(Produto, 'change', obj_id=self.produto.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produto.nome)

    # Testes para o modelo Pedido
    def test_pedido_changelist_view(self):
        url = self._get_admin_url(Pedido, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.pedido.pk)) # Pedido ID
        self.assertContains(response, self.pedido.produto.nome)

    def test_pedido_add_view_get(self):
        url = self._get_admin_url(Pedido, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar pedido")

    def test_pedido_change_view_get(self):
        url = self._get_admin_url(Pedido, 'change', obj_id=self.pedido.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.pedido.quantidade))

    # Testes para o modelo Avaliacao
    def test_avaliacao_changelist_view(self):
        url = self._get_admin_url(Avaliacao, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.avaliacao.produto.nome)
        self.assertContains(response, str(self.avaliacao.nota))

    def test_avaliacao_add_view_get(self):
        url = self._get_admin_url(Avaliacao, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar avaliação")

    def test_avaliacao_change_view_get(self):
        url = self._get_admin_url(Avaliacao, 'change', obj_id=self.avaliacao.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.avaliacao.comentario)

    # Testes para o modelo RespostaVendedorAvaliacao
    def test_respostavendedoravaliacao_changelist_view(self):
        url = self._get_admin_url(RespostaVendedorAvaliacao, 'changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.resposta_avaliacao.texto)

    def test_respostavendedoravaliacao_add_view_get(self):
        url = self._get_admin_url(RespostaVendedorAvaliacao, 'add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adicionar resposta vendedor avaliacao")

    def test_respostavendedoravaliacao_change_view_get(self):
        url = self._get_admin_url(RespostaVendedorAvaliacao, 'change', obj_id=self.resposta_avaliacao.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.resposta_avaliacao.texto)

    # Testes para acesso não-admin (devem falhar)
    def test_non_admin_user_cannot_access_admin(self):
        self.client.logout() # Desloga o admin
        self.client.login(username='comprador_admin_test', password='testpassword')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302) # Deve redirecionar para o login
        self.assertTrue('/admin/login/' in response.url)

    def test_admin_user_must_be_staff(self):
        # Criar um usuário que não é superuser nem staff
        non_staff_user = User.objects.create_user(
            username='nonstaff', email='nonstaff@example.com', password='nonstaffpassword'
        )
        self.client.logout()
        self.client.login(username='nonstaff', password='nonstaffpassword')
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302) # Deve redirecionar para o login do admin
        self.assertTrue('/admin/login/' in response.url)