from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from marketplace.models import PerfilComprador, PerfilVendedor, Produto, Pedido # Remova Reporte se não existir
from marketplace.forms import UserEditForm, ProdutoForm

URL_COMPRADOR_CADASTRO = reverse('marketplace:comprador_cadastro')
URL_COMPRADOR_LOGIN = reverse('marketplace:comprador_login')
URL_COMPRADOR_LOGOUT = reverse('marketplace:comprador_logout')
URL_PAGINA_INICIAL_COMPRADOR = reverse('marketplace:pagina_inicial_comprador')
URL_COMPRADOR_DESEJOS_LISTA = reverse('marketplace:comprador_desejos_lista')

URL_VENDEDOR_CADASTRO = reverse('marketplace:vendedor_cadastro')
URL_VENDEDOR_LOGIN = reverse('marketplace:vendedor_login')
URL_VENDEDOR_LOGOUT = reverse('marketplace:vendedor_logout')
URL_VENDEDOR_DASHBOARD = reverse('marketplace:vendedor_dashboard')
URL_VENDEDOR_PRODUTOS = reverse('marketplace:vendedor_produtos')
URL_VENDEDOR_ADICIONAR_PRODUTO = reverse('marketplace:vendedor_adicionar_produto')

URL_LANDING_PAGE = reverse('marketplace:landing_page')

URL_ADMIN_DASHBOARD = reverse('marketplace:admin_dashboard')
URL_ADMIN_LOGIN = reverse('marketplace:admin_login')
URL_ADMIN_LOGOUT = reverse('marketplace:admin_logout')
URL_ADMIN_USUARIOS = reverse('marketplace:admin_usuarios')
URL_ADMIN_ANUNCIOS = reverse('marketplace:admin_anuncios')
URL_ADMIN_PEDIDOS = reverse('marketplace:admin_pedidos')
URL_ADMIN_PEDIDOS_FINALIZADOS = reverse('marketplace:admin_pedidos_finalizados')
URL_ADMIN_REPORTES = reverse('marketplace:admin_reportes')
URL_ADMIN_REPORTES_ARQUIVADOS = reverse('marketplace:admin_reportes_arquivados')

def url_comprador_produto_detalhes(produto_id):
    return reverse('marketplace:comprador_produto_detalhes', args=[produto_id])

def url_vendedor_editar_produto(produto_id):
    return reverse('marketplace:vendedor_editar_produto', args=[produto_id])

def url_vendedor_excluir_produto(produto_id):
    return reverse('marketplace:vendedor_excluir_produto', args=[produto_id])

def url_admin_gerenciar_usuario(user_id):
    return reverse('marketplace:admin_gerenciar_usuario', args=[user_id])

def url_admin_excluir_usuario(user_id):
    return reverse('marketplace:admin_excluir_usuario', args=[user_id])

def url_admin_gerenciar_anuncio(produto_id):
    return reverse('marketplace:admin_gerenciar_anuncio', args=[produto_id])

def url_admin_excluir_anuncio(produto_id):
    return reverse('marketplace:admin_excluir_anuncio', args=[produto_id])

def url_admin_gerenciar_pedido(pedido_id):
    return reverse('marketplace:admin_gerenciar_pedido', args=[pedido_id])

def url_admin_gerenciar_reporte(reporte_id):
    return reverse('marketplace:admin_gerenciar_reporte', args=[reporte_id])


# # class TestViewsComprador(TestCase):
# #     def setUp(self):
# #         self.client = Client()
# #         self.comprador_login_credentials = {
# #             'username': 'comprador_login@teste.com',
# #             'password': 'passwordsegura'
# #         }
# #         self.comprador_group, _ = Group.objects.get_or_create(name='Compradores')
# #         self.user_comprador_para_login = User.objects.create_user(
# #             username='comprador_login@teste.com',
# #             email='comprador_login@teste.com',
# #             password='passwordsegura',
# #             first_name='Comprador De Login'
# #         )
# #         self.user_comprador_para_login.groups.add(self.comprador_group)
# #         PerfilComprador.objects.create(user=self.user_comprador_para_login, idade=20, cpf="12312312312", curso="TI", ra="RA001")

# #     @classmethod
# #     def setUpTestData(cls):
# #         User.objects.create_user(username='existente_comprador@email.com', email='existente_comprador@email.com', password='password123')

# #     def test_tela_comprador_cadastro_acessivel(self):
# #         response = self.client.get(URL_COMPRADOR_CADASTRO)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertTemplateUsed(response, 'comprador/cadastro.html')

# #     def test_cadastro_comprador_sucesso(self):
# #         comprador_data_para_cadastro = {
# #             'nome': 'Novo Comprador Cadastro', 'idade': 25, 'cpf': '11122233344',
# #             'curso': 'Engenharia de Testes', 'ra': 'RACOMP001',
# #             'email': 'novo_comprador_cad@teste.com', 'senha': 'TestandoSenha123!',
# #             'confirmar_senha': 'TestandoSenha123!'
# #         }
# #         response = self.client.post(URL_COMPRADOR_CADASTRO, data=comprador_data_para_cadastro)
    
# #         form_errors = response.context.get('form').errors if response.status_code == 200 and response.context and response.context.get('form') else None
# #         self.assertEqual(response.status_code, 302, f"Cadastro falhou. Erros do formulário: {form_errors}")
# #         self.assertRedirects(response, URL_PAGINA_INICIAL_COMPRADOR)

# #         self.assertTrue(User.objects.filter(username='novo_comprador_cad@teste.com').exists())
# #         novo_usuario = User.objects.get(username='novo_comprador_cad@teste.com')
# #         self.assertEqual(novo_usuario.first_name, 'Novo Comprador Cadastro')
# #         self.assertTrue(PerfilComprador.objects.filter(user=novo_usuario).exists())
# #         perfil = PerfilComprador.objects.get(user=novo_usuario)
# #         self.assertEqual(perfil.idade, 25)
# #         self.assertEqual(perfil.cpf, '11122233344')
# #         self.assertTrue(novo_usuario.groups.filter(name='Compradores').exists())

# #     def test_cadastro_comprador_email_existente(self):
# #         comprador_data_email_existente = {
# #             'nome': 'Comprador Email Repetido', 'idade': 22, 'cpf': '55566677788',
# #             'curso': 'Letras', 'ra': 'RALET01', 'email': 'existente_comprador@email.com',
# #             'senha': 'UmaSenhaQualquer1', 'confirmar_senha': 'UmaSenhaQualquer1'
# #         }
# #         response = self.client.post(URL_COMPRADOR_CADASTRO, data=comprador_data_email_existente)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertContains(response, "Este email já está cadastrado")

# #     def test_cadastro_comprador_senhas_nao_coincidem(self):
# #         comprador_data_senhas_divergentes = {
# #             'nome': 'Comprador Senhas Erradas', 'idade': 23, 'cpf': '10101010101',
# #             'curso': 'Musica', 'ra': 'RAMUS01', 'email': 'senhaserradas@teste.com',
# #             'senha': 'senhaA', 'confirmar_senha': 'senhaB'
# #         }
# #         response = self.client.post(URL_COMPRADOR_CADASTRO, data=comprador_data_senhas_divergentes)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertContains(response, "As senhas não coincidem")

# #     def test_cadastro_comprador_campo_nome_faltando(self):
# #         comprador_data_sem_nome = {
# #             'idade': 25, 'cpf': '11122233344', 'curso': 'Engenharia', 'ra': 'RACOMP00X',
# #             'email': 'semnome@teste.com', 'senha': 'TestandoSenha123!',
# #             'confirmar_senha': 'TestandoSenha123!'
# #         }
# #         response = self.client.post(URL_COMPRADOR_CADASTRO, data=comprador_data_sem_nome)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertContains(response, "Este campo é obrigatório.")
# #         form_errors = response.context['form'].errors
# #         self.assertIn('nome', form_errors)

# #     def test_tela_comprador_login_acessivel(self):
# #         response = self.client.get(URL_COMPRADOR_LOGIN)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertTemplateUsed(response, 'comprador/login.html')

# #     def test_login_comprador_sucesso(self):
# #         response = self.client.post(URL_COMPRADOR_LOGIN, data=self.comprador_login_credentials)
# #         self.assertEqual(response.status_code, 302)
# #         self.assertRedirects(response, URL_PAGINA_INICIAL_COMPRADOR)
# #         self.assertEqual(int(self.client.session['_auth_user_id']), self.user_comprador_para_login.pk)

# #     def test_login_comprador_senha_incorreta(self):
# #         credentials_erradas = self.comprador_login_credentials.copy()
# #         credentials_erradas['password'] = 'senhaerrada'
# #         response = self.client.post(URL_COMPRADOR_LOGIN, data=credentials_erradas)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertContains(response, "Email e/ou senha inválidos.")
# #         self.assertNotIn('_auth_user_id', self.client.session)

# #     def test_login_comprador_usuario_inexistente(self):
# #         credentials_inexistentes = {
# #             'username': 'naoexiste@teste.com',
# #             'password': 'passwordqualquer'
# #         }
# #         response = self.client.post(URL_COMPRADOR_LOGIN, data=credentials_inexistentes)
# #         self.assertEqual(response.status_code, 200)
# #         self.assertContains(response, "Email e/ou senha inválidos.")
# #         self.assertNotIn('_auth_user_id', self.client.session)

# # class TestViewsVendedor(TestCase):
    def setUp(self):
        self.client = Client()
        self.vendedor_login_credentials = {
            'username': 'vendedor_login@teste.com',
            'password': 'passwordvendedor'
        }
        self.vendedor_group, _ = Group.objects.get_or_create(name='Vendedores')
        self.user_vendedor_para_login = User.objects.create_user(
            username='vendedor_login@teste.com',
            email='vendedor_login@teste.com',
            password='passwordvendedor',
            first_name='Vendedor De Login'
        )
        self.user_vendedor_para_login.groups.add(self.vendedor_group)
        PerfilVendedor.objects.create(user=self.user_vendedor_para_login, idade=30, cpf="32132132132", curso="ADM", ra="RAV002")

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='existente_vendedor@email.com', email='existente_vendedor@email.com', password='password123')

    def test_tela_vendedor_cadastro_acessivel(self):
        response = self.client.get(URL_VENDEDOR_CADASTRO)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vendedor/cadastro.html')

    def test_cadastro_vendedor_sucesso(self):
        vendedor_data_para_cadastro = {
            'nome': 'Novo Vendedor Cadastro', 'idade': 30, 'cpf': '98765432109',
            'curso': 'Administracao de Vendas', 'ra': 'RAVEND001',
            'email': 'novo_vendedor_cad@teste.com', 'senha': 'TestandoVendedor123!',
            'confirmar_senha': 'TestandoVendedor123!'
        }
        response = self.client.post(URL_VENDEDOR_CADASTRO, data=vendedor_data_para_cadastro)
        
        form_errors = response.context.get('form').errors if response.status_code == 200 and response.context and response.context.get('form') else None
        self.assertEqual(response.status_code, 302, f"Cadastro falhou. Erros do formulário: {form_errors}")
        self.assertRedirects(response, URL_VENDEDOR_DASHBOARD)

        self.assertTrue(User.objects.filter(username='novo_vendedor_cad@teste.com').exists())
        novo_vendedor = User.objects.get(username='novo_vendedor_cad@teste.com')
        self.assertEqual(novo_vendedor.first_name, 'Novo Vendedor Cadastro')
        self.assertFalse(novo_vendedor.is_staff)
        self.assertTrue(PerfilVendedor.objects.filter(user=novo_vendedor).exists())
        perfil_vend = PerfilVendedor.objects.get(user=novo_vendedor)
        self.assertEqual(perfil_vend.idade, 30)
        self.assertEqual(perfil_vend.ra, 'RAVEND001')
        self.assertTrue(novo_vendedor.groups.filter(name='Vendedores').exists())

    def test_cadastro_vendedor_email_existente(self):
        vendedor_data_email_existente = {
            'nome': 'Vendedor Email Repetido', 'idade': 32, 'cpf': '22233344455',
            'curso': 'Marketing', 'ra': 'RAMKT01', 'email': 'existente_vendedor@email.com',
            'senha': 'OutraSenha123', 'confirmar_senha': 'OutraSenha123'
        }
        response = self.client.post(URL_VENDEDOR_CADASTRO, data=vendedor_data_email_existente)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este email já está cadastrado")

    def test_cadastro_vendedor_senhas_nao_coincidem(self):
        vendedor_data_senhas_divergentes = {
            'nome': 'Vendedor Senhas Erradas', 'idade': 28, 'cpf': '77788899900',
            'curso': 'Eventos', 'ra': 'RAEVN01', 'email': 'vend_senhaserradas@teste.com',
            'senha': 'senhaX', 'confirmar_senha': 'senhaY'
        }
        response = self.client.post(URL_VENDEDOR_CADASTRO, data=vendedor_data_senhas_divergentes)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "As senhas não coincidem")

    def test_cadastro_vendedor_campo_cpf_faltando(self):
        vendedor_data_sem_cpf = {
            'nome': 'Vendedor Sem CPF', 'idade': 30,
            'curso': 'Administracao', 'ra': 'RAVEND00X',
            'email': 'semcpf@teste.com', 'senha': 'TestandoVendedor123!',
            'confirmar_senha': 'TestandoVendedor123!'
        }
        response = self.client.post(URL_VENDEDOR_CADASTRO, data=vendedor_data_sem_cpf)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo é obrigatório.")
        form_errors = response.context['form'].errors
        self.assertIn('cpf', form_errors)

    def test_tela_vendedor_login_acessivel(self):
        response = self.client.get(URL_VENDEDOR_LOGIN)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vendedor/login.html')

    def test_login_vendedor_sucesso(self):
        response = self.client.post(URL_VENDEDOR_LOGIN, data=self.vendedor_login_credentials)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, URL_VENDEDOR_DASHBOARD)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user_vendedor_para_login.pk)

    def test_login_vendedor_senha_incorreta(self):
        credentials_erradas = self.vendedor_login_credentials.copy()
        credentials_erradas['password'] = 'senhaerrada_vendedor'
        response = self.client.post(URL_VENDEDOR_LOGIN, data=credentials_erradas)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email e/ou senha inválidos.")
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_vendedor_usuario_inexistente(self):
        credentials_inexistentes = {
            'username': 'naoexistevend@teste.com',
            'password': 'passwordqualquer_vend'
        }
        response = self.client.post(URL_VENDEDOR_LOGIN, data=credentials_inexistentes)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email e/ou senha inválidos.")
        self.assertNotIn('_auth_user_id', self.client.session)


class TestViewsAdmin(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_teste@email.com',
            email='admin_teste@email.com',
            password='adminpassword'
        )
        self.comprador_group, _ = Group.objects.get_or_create(name='Compradores')
        self.vendedor_group, _ = Group.objects.get_or_create(name='Vendedores')

        self.user_comprador1 = User.objects.create_user(username='comprador1@teste.com', password='password', first_name='Comprador Um')
        self.user_comprador1.groups.add(self.comprador_group)
        PerfilComprador.objects.create(user=self.user_comprador1, idade=20, cpf="11122233344", curso="C1", ra="RA1")

        self.user_vendedor1 = User.objects.create_user(username='vendedor1@teste.com', password='password', first_name='Vendedor Um')
        self.user_vendedor1.groups.add(self.vendedor_group)
        PerfilVendedor.objects.create(user=self.user_vendedor1, idade=30, cpf="22233344455", curso="C2", ra="RA2")

        self.produto1 = Produto.objects.create(vendedor=self.user_vendedor1, nome="Produto Teste Admin", descricao="Desc P1", preco="10.00", estoque=5)
        self.pedido1 = Pedido.objects.create(vendedor=self.user_vendedor1, cliente=self.user_comprador1, produto=self.produto1, quantidade=1, status='pendente')
        # self.reporte1 = Reporte.objects.create(usuario_reportou=self.user_comprador1, produto_reportado=self.produto1, titulo="Reporte Teste", descricao="Desc R1", status='aberto')


    def test_admin_login_page_loads(self):
        response = self.client.get(URL_ADMIN_LOGIN)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')

    def test_admin_login_success(self):
        response = self.client.post(URL_ADMIN_LOGIN, {'username': 'admin_teste@email.com', 'password': 'adminpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, URL_ADMIN_DASHBOARD)
        self.assertIn('_auth_user_id', self.client.session)

    def test_admin_login_failure_wrong_password(self):
        response = self.client.post(URL_ADMIN_LOGIN, {'username': 'admin_teste@email.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credenciais inválidas ou sem permissão")
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_login_failure_not_staff(self):
        response = self.client.post(URL_ADMIN_LOGIN, {'username': 'comprador1@teste.com', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credenciais inválidas ou sem permissão")
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(URL_ADMIN_DASHBOARD)
        self.assertEqual(response.status_code, 302)
        self.assertIn(URL_ADMIN_LOGIN, response.url)

    def test_admin_dashboard_loads_if_logged_in_as_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(URL_ADMIN_DASHBOARD)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')
        self.assertContains(response, "Últimos Usuários Cadastrados")
        self.assertIn('recent_users', response.context)
        self.assertIn('recent_products', response.context)
        self.assertIn('chart_labels', response.context)

    def test_admin_logout(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get(URL_ADMIN_LOGOUT, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, URL_ADMIN_LOGIN, status_code=302, target_status_code=200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_usuarios_page_loads_for_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(URL_ADMIN_USUARIOS)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/usuarios.html')
        self.assertContains(response, self.user_comprador1.username)

    def test_admin_gerenciar_usuario_page_loads_for_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(url_admin_gerenciar_usuario(self.user_comprador1.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/gerenciar_usuario.html')
        self.assertContains(response, self.user_comprador1.username)
        self.assertIsInstance(response.context['user_form'], UserEditForm)

    def test_admin_gerenciar_usuario_update_success(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        user_to_edit = self.user_comprador1
        new_first_name = "Comprador Um Editado"
        
        user_data = {
            'first_name': new_first_name,
            'last_name': user_to_edit.last_name if user_to_edit.last_name else '',
            'email': user_to_edit.email,
            'is_active': user_to_edit.is_active,
            'is_staff': user_to_edit.is_staff,
            'groups': [g.pk for g in user_to_edit.groups.all()]
        }
        profile_data = {
            'comprador-idade': 22,
            'comprador-cpf': '11100011100',
            'comprador-curso': 'Curso Editado',
            'comprador-ra': 'RAEditado'
        }
        post_data = {**user_data, **profile_data}

        response = self.client.post(url_admin_gerenciar_usuario(user_to_edit.id), data=post_data)
        
        if response.status_code != 302:
             user_form_errors = response.context.get('user_form').errors if response.context.get('user_form') else "No user_form errors"
             pc_form_errors = response.context.get('perfil_comprador_form').errors if response.context.get('perfil_comprador_form') else "No perfil_comprador_form errors"
             pv_form_errors = response.context.get('perfil_vendedor_form').errors if response.context.get('perfil_vendedor_form') else "No perfil_vendedor_form errors"
             print(f"User form errors: {user_form_errors}")
             print(f"Perfil Comprador form errors: {pc_form_errors}")
             print(f"Perfil Vendedor form errors: {pv_form_errors}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, URL_ADMIN_USUARIOS)

        user_to_edit.refresh_from_db()
        self.assertEqual(user_to_edit.first_name, new_first_name)
        
        perfil = PerfilComprador.objects.get(user=user_to_edit)
        self.assertEqual(perfil.idade, 22)
        self.assertEqual(perfil.curso, 'Curso Editado')

    def test_admin_excluir_usuario_page_loads_and_confirm(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        user_to_delete_id = self.user_comprador1.id
        
        response_get = self.client.get(url_admin_excluir_usuario(user_to_delete_id))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'admin/confirmar_exclusao_usuario.html')
        self.assertContains(response_get, self.user_comprador1.username)

        response_post = self.client.post(url_admin_excluir_usuario(user_to_delete_id))
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, URL_ADMIN_USUARIOS)
        self.assertFalse(User.objects.filter(id=user_to_delete_id).exists())

    def test_admin_cannot_delete_self(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.post(url_admin_excluir_usuario(self.admin_user.id))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, URL_ADMIN_USUARIOS)
        self.assertTrue(User.objects.filter(id=self.admin_user.id).exists())
        
        response_followed = self.client.get(response.url, follow=True)
        # A forma de verificar mensagens depende de como você configurou o MESSAGE_STORAGE
        # Se estiver usando o FallbackStorage ou SessionStorage, as mensagens estarão no contexto após o redirect
        # Esta é uma forma mais simples de verificar, assumindo que a mensagem é renderizada na página de destino
        # self.assertContains(response_followed, "Você não pode excluir sua própria conta") 
        # Para um teste mais robusto de mensagens:
        messages = list(response_followed.context.get('messages', []))
        self.assertTrue(any(message.level == 40 and "Você não pode excluir sua própria conta" in message.message for message in messages))


    def test_admin_anuncios_page_loads_for_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(URL_ADMIN_ANUNCIOS)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/anuncios.html')
        self.assertContains(response, self.produto1.nome)

    def test_admin_gerenciar_anuncio_page_loads_for_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(url_admin_gerenciar_anuncio(self.produto1.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/gerenciar_anuncio.html')
        self.assertContains(response, self.produto1.nome)
        self.assertIsInstance(response.context['form'], ProdutoForm)
        
    def test_admin_gerenciar_anuncio_update_success(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        produto_a_editar = self.produto1
        novo_nome = "Produto Editado pelo Admin"
        novo_preco = "15.99"
        post_data = {
            'nome': novo_nome,
            'descricao': produto_a_editar.descricao,
            'preco': novo_preco,
            'estoque': produto_a_editar.estoque
        }
        response = self.client.post(url_admin_gerenciar_anuncio(produto_a_editar.id), data=post_data)
        if response.status_code != 302 and response.context and response.context.get('form'):
            print(f"Anuncio Edit Form Errors: {response.context.get('form').errors}")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, URL_ADMIN_ANUNCIOS)
        
        produto_a_editar.refresh_from_db()
        self.assertEqual(produto_a_editar.nome, novo_nome)
        self.assertEqual(str(produto_a_editar.preco), novo_preco)

    def test_admin_excluir_anuncio_page_loads_and_confirm(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        produto_a_excluir_id = self.produto1.id
        
        response_get = self.client.get(url_admin_excluir_anuncio(produto_a_excluir_id))
        self.assertEqual(response_get.status_code, 200)
        self.assertTemplateUsed(response_get, 'admin/confirmar_exclusao_anuncio.html')

        response_post = self.client.post(url_admin_excluir_anuncio(produto_a_excluir_id))
        self.assertEqual(response_post.status_code, 302)
        self.assertRedirects(response_post, URL_ADMIN_ANUNCIOS)
        self.assertFalse(Produto.objects.filter(id=produto_a_excluir_id).exists())

    def test_admin_pedidos_page_loads_for_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(URL_ADMIN_PEDIDOS)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/pedidos.html')
        self.assertContains(response, f"<td>{self.pedido1.id}</td>") # Nova asserção

    def test_admin_gerenciar_pedido_page_loads_for_staff(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        response = self.client.get(url_admin_gerenciar_pedido(self.pedido1.id))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/gerenciar_pedido.html')
        self.assertContains(response, f"Gerenciar Pedido #{self.pedido1.id}")
        self.assertEqual(response.context['pedido'], self.pedido1)

    def test_admin_gerenciar_pedido_update_status_success(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        novo_status = 'enviado' # Um status válido das suas choices
        
        url_do_post = url_admin_gerenciar_pedido(self.pedido1.id)

        # Faça a requisição POST e siga o redirect automaticamente
        response_final = self.client.post(url_do_post, data={'status': novo_status}, follow=True)
        
        # Verifique se a página final (após o redirect) tem status 200
        self.assertEqual(response_final.status_code, 200, 
                         f"A página final após o redirect não carregou. Status: {response_final.status_code}")
        
        # Verifique se o redirect ocorreu para a URL correta
        # response_final.redirect_chain contém uma lista de tuplas (url, status_code) dos redirects seguidos
        self.assertTrue(response_final.redirect_chain) # Garante que houve pelo menos um redirect
        self.assertEqual(response_final.redirect_chain[0][0], url_do_post, "A URL de redirect não foi a esperada.")
        self.assertEqual(response_final.redirect_chain[0][1], 302, "O status code do redirect não foi 302.")

        # Atualiza o objeto do pedido do banco de dados para pegar o novo status
        self.pedido1.refresh_from_db()
        self.assertEqual(self.pedido1.status, novo_status, "O status do pedido não foi atualizado no banco de dados.")
        
        # Agora, verifique as mensagens no contexto da response_final
        messages_list = list(response_final.context.get('messages', []))
        
        expected_message_text = f"Status do pedido #{self.pedido1.id} atualizado para '{self.pedido1.get_status_display()}'."

        found_message = False
        for message in messages_list:
            if expected_message_text in message.message:
                found_message = True
                break
        
        self.assertTrue(found_message,
                        f"Mensagem de sucesso esperada '{expected_message_text}' não foi encontrada na lista de mensagens: {[m.message for m in messages_list]}")


    def test_admin_pedidos_finalizados_page_loads(self):
        self.client.login(username='admin_teste@email.com', password='adminpassword')
        self.pedido1.status = 'entregue'
        self.pedido1.save()
        response = self.client.get(URL_ADMIN_PEDIDOS_FINALIZADOS)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/pedidos_finalizados.html')
        self.assertContains(response, f"<td>{self.pedido1.id}</td>") # Nova asserção, ou apenas self.pedido1.id se for suficiente

class LogoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.comprador_group, _ = Group.objects.get_or_create(name='Compradores')
        self.user_comprador = User.objects.create_user(username='logout_comprador@teste.com', password='password', first_name="Logout")
        self.user_comprador.groups.add(self.comprador_group)
        PerfilComprador.objects.create(user=self.user_comprador, idade=20, cpf="00011122233", curso="Logout", ra="RALOGOUT")
        
        self.vendedor_group, _ = Group.objects.get_or_create(name='Vendedores')
        self.user_vendedor = User.objects.create_user(username='logout_vendedor@teste.com', password='password', first_name="LogoutVend")
        self.user_vendedor.groups.add(self.vendedor_group)
        PerfilVendedor.objects.create(user=self.user_vendedor, idade=30, cpf="44455566677", curso="Logout Vend", ra="RALOGOUTVEND")

    def test_logout_comprador(self):
        self.client.login(username='logout_comprador@teste.com', password='password')
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get(URL_COMPRADOR_LOGOUT, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, URL_LANDING_PAGE, status_code=302, target_status_code=200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, "Você saiu da sua conta.")

    def test_logout_vendedor(self):
        self.client.login(username='logout_vendedor@teste.com', password='password')
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get(URL_VENDEDOR_LOGOUT, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, URL_LANDING_PAGE, status_code=302, target_status_code=200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, "Você saiu da sua conta de vendedor.")