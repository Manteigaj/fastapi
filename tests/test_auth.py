from fastapi.testclient import TestClient

from app.models import Usuario
from app.security import bcrypt_context


def test_home(client: TestClient):
    response = client.get("/auth/")

    assert response.status_code == 200
    assert response.json() == {
        "mensagem": "voce acessou a rota padrao de autenticaçao",
        "autenticado": False,
    }


def test_criar_conta(client: TestClient):
    response = client.post(
        "/auth/criar_conta",
        json={
            "nome": "João",
            "email": "joao@email.com",
            "senha": "123456",
            "ativo": True,
            "admin": False,
        },
    )

    assert response.status_code == 200
    assert "usuário cadastrado com sucesso" in response.json()["mensagem"]


def test_criar_conta_email_existente(client: TestClient):
    usuario = {
        "nome": "João",
        "email": "joao@email.com",
        "senha": "123456",
        "ativo": True,
        "admin": False,
    }

    client.post("/auth/criar_conta", json=usuario)

    response = client.post("/auth/criar_conta", json=usuario)

    assert response.status_code == 400
    assert response.json()["detail"] == "E-mail do usuário já cadastrado"


def test_login_sucesso(client: TestClient, session):
    senha = bcrypt_context.hash("123456")

    usuario = Usuario(
        "João",
        "joao@email.com",
        senha,
        True,
        False,
    )

    session.add(usuario)
    session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "joao@email.com",
            "senha": "123456",
        },
    )

    dados = response.json()

    assert response.status_code == 200
    assert "access_token" in dados
    assert "refresh_token" in dados
    assert dados["token_type"] == "Bearer"


def test_login_credenciais_invalidas(client: TestClient):
    response = client.post(
        "/auth/login",
        json={
            "email": "naoexiste@email.com",
            "senha": "123456",
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"] == "Usuário não encontrado ou credenciais inválidas"
    )


def test_login_form(client: TestClient, session):
    senha = bcrypt_context.hash("123456")

    usuario = Usuario(
        "João",
        "joao@email.com",
        senha,
        True,
        False,
    )

    session.add(usuario)
    session.commit()

    response = client.post(
        "/auth/login-form",
        data={
            "username": "joao@email.com",
            "password": "123456",
        },
    )

    dados = response.json()

    assert response.status_code == 200
    assert "access_token" in dados
    assert "refresh_token" in dados
    assert dados["token_type"] == "Bearer"


def test_refresh_token(client: TestClient, session):
    senha = bcrypt_context.hash("123456")

    usuario = Usuario(
        "João",
        "joao@email.com",
        senha,
        True,
        False,
    )

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    login = client.post(
        "/auth/login",
        json={
            "email": "joao@email.com",
            "senha": "123456",
        },
    )

    refresh_token = login.json()["refresh_token"]

    response = client.get(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    dados = response.json()

    assert response.status_code == 200
    assert "access_token" in dados
    assert dados["token_type"] == "Bearer"
