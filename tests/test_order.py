from fastapi.testclient import TestClient

from app.auth_routes import criar_token
from app.models import Usuario, Pedido, ItensPedido
from app.security import bcrypt_context


def criar_usuario(session, admin=False):
    usuario = Usuario(
        nome="João",
        email="joao@email.com",
        senha=bcrypt_context.hash("123456"),
        ativo=True,
        admin=admin,
    )

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return usuario


def headers(usuario):
    token = criar_token(usuario.id)
    return {"Authorization": f"Bearer {token}"}


def test_home_pedidos(client: TestClient, session):
    usuario = criar_usuario(session)

    response = client.get(
        "/pedidos/",
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert response.json() == {"mensagem": "voce acessou a rota de pedidos"}


def test_criar_pedido(client, session):
    usuario = criar_usuario(session)

    response = client.post(
        "/pedidos/pedidos",
        json={
            "usuario": usuario.id,
        },
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert "Pedido criado com sucesso" in response.json()["mensagem"]


def test_cancelar_pedido(client, session):
    usuario = criar_usuario(session)

    pedido = Pedido(usuario_id=usuario.id)

    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    response = client.post(
        f"/pedidos/pedido/cancelar/{pedido.id}",
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert response.json()["pedido"]["status"] == "CANCELADO"


def test_cancelar_pedido_inexistente(client, session):
    usuario = criar_usuario(session)

    response = client.post(
        "/pedidos/pedido/cancelar/999",
        headers=headers(usuario),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "pedido não encontrado"


def test_listar_pedidos_admin(client, session):
    admin = criar_usuario(session, admin=True)

    pedido = Pedido(usuario_id=admin.id)

    session.add(pedido)
    session.commit()

    response = client.get(
        "/pedidos/listar",
        headers=headers(admin),
    )

    assert response.status_code == 200
    assert len(response.json()["pedidos"]) == 1


def test_listar_pedidos_sem_permissao(client, session):
    usuario = criar_usuario(session)

    response = client.get(
        "/pedidos/listar",
        headers=headers(usuario),
    )

    assert response.status_code == 401


def test_adicionar_item(client, session):
    usuario = criar_usuario(session)

    pedido = Pedido(usuario_id=usuario.id)

    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    response = client.post(
        f"/pedidos/pedido/adicionar-item/{pedido.id}",
        json={
            "quantidade": 2,
            "sabor": "Calabresa",
            "tamanho": "Grande",
            "preco_unitario": 50,
        },
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert response.json()["mensagem"] == "item criado com sucesso"


def test_remover_item(client, session):
    usuario = criar_usuario(session)

    pedido = Pedido(usuario_id=usuario.id)

    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    item = ItensPedido(
        quantidade=1,
        sabor="Calabresa",
        tamanho="Grande",
        preco_unitario=50,
        pedido_id=pedido.id,
    )

    session.add(item)
    session.commit()
    session.refresh(item)

    response = client.post(
        f"/pedidos/pedido/remover-item/{item.id}",
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert response.json()["mensagem"] == "item removido com sucesso"


def test_finalizar_pedido(client, session):
    usuario = criar_usuario(session)

    pedido = Pedido(usuario_id=usuario.id)

    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    response = client.post(
        f"/pedidos/pedido/finalizar/{pedido.id}",
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert response.json()["pedido"]["status"] == "Finalizado"


def test_visualizar_pedido(client, session):
    usuario = criar_usuario(session)

    pedido = Pedido(usuario_id=usuario.id)

    session.add(pedido)
    session.commit()
    session.refresh(pedido)

    response = client.get(
        f"/pedidos/pedido/{pedido.id}",
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert "pedido" in response.json()


def test_listar_pedidos_usuario(client, session):
    usuario = criar_usuario(session)

    pedido = Pedido(usuario_id=usuario.id)

    session.add(pedido)
    session.commit()

    response = client.get(
        "/pedidos/listar/pedidos-usuario",
        headers=headers(usuario),
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
