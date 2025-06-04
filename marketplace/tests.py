from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.conf import settings
import importlib
from django.contrib.auth import get_user_model
from django.utils import timezone # Se precisar lidar com datas/horas
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
import os

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

User = get_user_model()

# Mantenha suas outras classes de teste (UserModelTests, ViewTests, etc.) como estavam,
# ou me diga se você quer que eu as reescreva também.
# O código abaixo foca em refazer a ViewsAdminTests.

class ViewsAdminTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # ... (criação de usuários e category como antes) ...
        cls.admin_password = 'admin_pass_secure' # Exemplo de senha
        admin_obj = User.objects.create_superuser(
            username='test_superadmin_setup', # Nome de usuário único
            email='test_superadmin_setup@example.com',
            password=cls.admin_password
        )
        admin_obj.user_type = 'admin'
        admin_obj.save()
        cls.admin_user = admin_obj

        cls.vendor_password = 'vendor_pass_secure' # Exemplo
        vendor_obj = User.objects.create_user(
            username='test_adminview_vendor_setup', # Nome de usuário único
            email='test_adminview_vendor_setup@example.com',
            password=cls.vendor_password
        )
        vendor_obj.user_type = 'vendedor'
        vendor_obj.save()
        cls.vendor_user = vendor_obj

        cls.buyer_password = 'buyer_pass_secure' # Exemplo
        buyer_obj = User.objects.create_user(
            username='test_adminview_buyer_setup', # Nome de usuário único
            email='test_adminview_buyer_setup@example.com',
            password=cls.buyer_password
        )
        buyer_obj.user_type = 'comprador'
        buyer_obj.save()
        cls.buyer_user = buyer_obj

        cls.category1 = Category.objects.create(name='Categoria Teste Admin Setup 1')
        cls.category2 = Category.objects.create(name='Categoria Teste Admin Setup 2')


        # Produto (CORRIGIDO: sem 'disponivel')
        cls.test_image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        cls.produto1 = Produto.objects.create(
            vendedor=cls.vendor_user,
            category=cls.category1,
            nome='Produto Teste Admin Setup A', # Nome único para o produto
            descricao='Descrição do Produto Teste Admin Setup A.',
            preco=Decimal('199.99'),
            estoque=10,
            imagem=SimpleUploadedFile(name='prod_admin_setup_a.jpg', content=cls.test_image_content, content_type='image/jpeg')
            # removido 'disponivel=True' pois não existe no modelo Produto fornecido
        )

        # Pedido (CORRIGIDO: 'cliente' em vez de 'comprador', e sem 'preco_total')
        cls.pedido1 = Pedido.objects.create(
            vendedor=cls.vendor_user,
            cliente=cls.buyer_user, # CORRIGIDO
            produto=cls.produto1,
            quantidade=1,
            status='Pendente'
            # 'preco_total' é uma @property, não um campo de banco de dados para ser definido aqui
        )

        # ... (URLs como antes) ...
        cls.login_url_admin = reverse('marketplace:admin_login')
        cls.dashboard_url_admin = reverse('marketplace:admin_dashboard')
        cls.users_url_admin = reverse('marketplace:admin_usuarios')
        cls.anuncios_url_admin = reverse('marketplace:admin_anuncios')
        cls.pedidos_url_admin = reverse('marketplace:admin_pedidos')
        cls.pedidos_finalizados_url_admin = reverse('marketplace:admin_pedidos_finalizados')

    def setUp(self):
        self.client = Client()

    def _login_as_admin_user(self):
        self.client.login(email=self.admin_user.email, password=self.admin_password)

    def _assert_admin_redirects_to_login(self, url_to_check, response_from_get):
        expected_redirect = f"{self.login_url_admin}?next={url_to_check}"
        self.assertRedirects(response_from_get, expected_redirect, status_code=302)

    # --- Testes de Login/Logout do Admin ---
    def test_admin_login_page_get(self):
        response = self.client.get(self.login_url_admin)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html') # Confirme o template

    def test_admin_logout_view(self):
        self._login_as_admin_user()
        response = self.client.get(reverse('marketplace:admin_logout')) # Confirme o nome da URL de logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # --- Testes de Acesso a Páginas Admin ---
    def test_admin_dashboard_access(self):
        # Não autenticado
        response_unauth = self.client.get(self.dashboard_url_admin)
        self._assert_admin_redirects_to_login(self.dashboard_url_admin, response_unauth)

        # Autenticado como não-admin (ex: vendedor)
        self.client.login(email=self.vendor_user.email, password=self.vendor_password)
        response_non_admin = self.client.get(self.dashboard_url_admin)
        self._assert_admin_redirects_to_login(self.dashboard_url_admin, response_non_admin)
        self.client.logout() # Logout para o próximo teste

        # Autenticado como admin
        self._login_as_admin_user()
        response_admin = self.client.get(self.dashboard_url_admin)
        self.assertEqual(response_admin.status_code, 302)

    # --- Testes de Funcionalidades (Exemplos) ---

    def tearDown(self):
        # Limpeza opcional de arquivos de imagem criados, se necessário
        produtos_teste = Produto.objects.filter(nome__icontains='(AdminTest)') | Produto.objects.filter(nome__icontains='Admin A')
        for p in produtos_teste:
            if p.imagem and hasattr(p.imagem, 'path'):
                if os.path.exists(p.imagem.path):
                    try:
                        os.remove(p.imagem.path)
                    except OSError:
                        pass # Ignorar erros se o arquivo não puder ser removido
        super().tearDown()