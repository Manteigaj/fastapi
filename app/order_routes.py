from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import pegar_sessao, verificar_token
from app.models import Pedido, Usuario, ItensPedido
from app.schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema

order_router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"],
    dependencies=[Depends(verificar_token)],
)


@order_router.get("/")
async def pedidos():
    return {"mensagem": "voce acessou a rota de pedidos"}


@order_router.post("/pedidos")
async def criar_pedido(
    pedido_schema: PedidoSchema,
    session: Session = Depends(pegar_sessao),
):
    novo_pedido = Pedido(usuario_id=pedido_schema.usuario)

    session.add(novo_pedido)
    session.commit()

    return {"mensagem": f"Pedido criado com sucesso. ID do Pedido: {novo_pedido.id}"}


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.scalar(select(Pedido).where(Pedido.id == id_pedido))

    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para fazer essa modificação",
        )

    pedido.status = "CANCELADO"
    session.commit()

    return {
        "mensagem": f"Pedido número: {pedido.id} cancelado com sucesso",
        "pedido": pedido,
    }


@order_router.get("/listar")
async def listar_pedidos(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    if not usuario.admin:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para acessar essa rota",
        )

    pedidos = session.scalars(select(Pedido)).all()

    return {"pedidos": pedidos}


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.scalar(select(Pedido).where(Pedido.id == id_pedido))

    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não existente")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para fazer essa operação",
        )

    item_pedido = ItensPedido(
        quantidade=item_pedido_schema.quantidade,
        sabor=item_pedido_schema.sabor,
        tamanho=item_pedido_schema.tamanho,
        preco_unitario=item_pedido_schema.preco_unitario,
        pedido_id=id_pedido,
    )

    session.add(item_pedido)

    pedido.calcular_preco()

    session.commit()

    return {
        "mensagem": "item criado com sucesso",
        "item_id": item_pedido.id,
        "preco_pedido": pedido.preco,
    }


@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(
    id_item_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    item_pedido = session.scalar(
        select(ItensPedido).where(ItensPedido.id == id_item_pedido)
    )

    if item_pedido is None:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    pedido = session.scalar(select(Pedido).where(Pedido.id == item_pedido.pedido_id))

    if pedido is None:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para fazer essa operação",
        )

    session.delete(item_pedido)

    pedido.calcular_preco()

    session.commit()

    return {
        "mensagem": "item removido com sucesso",
        "quantidade_itens_pedido": len(pedido.itens),
        "pedido": pedido,
    }


@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.scalar(select(Pedido).where(Pedido.id == id_pedido))

    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para fazer essa modificação",
        )

    pedido.status = "Finalizado"

    session.commit()

    return {
        "mensagem": f"Pedido número: {pedido.id} finalizado com sucesso",
        "pedido": pedido,
    }


@order_router.get("/pedido/{id_pedido}")
async def visualizar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.scalar(select(Pedido).where(Pedido.id == id_pedido))

    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não encontrado")

    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para fazer essa modificação",
        )

    return {
        "quantidade de itens": len(pedido.itens),
        "pedido": pedido,
    }


@order_router.get(
    "/listar/pedidos-usuario",
    response_model=List[ResponsePedidoSchema],
)
async def listar_pedidos_usuario(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedidos = session.scalars(
        select(Pedido).where(Pedido.usuario_id == usuario.id)
    ).all()

    return pedidos
