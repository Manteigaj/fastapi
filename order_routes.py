from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao, verificar_token
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema
from models import Pedido, Usuario, ItensPedido
from typing import List

order_router = APIRouter(
    prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)]
)


@order_router.get("/")
async def pedidos():
    return {"mensagem": "voce acessou a rota de pedidos"}


@order_router.post("/pedidos")
async def criar_pedido(
    pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)
):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {"mensagem": f"Pedido criado com sucesso. ID do Pedido: {novo_pedido.id}"}


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(
    id_pedido: int,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
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
            status_code=401, detail="Você não tem autorização para acessar essa rota"
        )
    else:
        pedidos = session.query(Pedido).all()
        return {"pedidos": pedidos}


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(
    id_pedido: int,
    item_pedido_schema: ItemPedidoSchema,
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não existente")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401, detail="Você não tem autorização para fazer essa operação"
        )
    item_pedido = ItensPedido(
        item_pedido_schema.quantidade,
        item_pedido_schema.sabor,
        item_pedido_schema.tamanho,
        item_pedido_schema.preco_unitario,
        id_pedido,
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
    item_pedido = (
        session.query(ItensPedido).filter(ItensPedido.id == id_item_pedido).first()
    )
    if item_pedido is None:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")
    pedido = session.query(Pedido).filter(Pedido.id == item_pedido.pedido).first()
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401, detail="Você não tem autorização para fazer essa operação"
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
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
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
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if pedido is None:
        raise HTTPException(status_code=400, detail="pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario:
        raise HTTPException(
            status_code=401,
            detail="Você não tem autorização para fazer essa modificação",
        )
    return {"quantidade de itens": len(pedido.itens), "pedido": pedido}


@order_router.get("/listar/pedidos-usuario", response_model=List[ResponsePedidoSchema])
async def listar_pedidos_usuario(
    session: Session = Depends(pegar_sessao),
    usuario: Usuario = Depends(verificar_token),
):
    pedidos = session.query(Pedido).filter(Pedido.usuario == usuario.id).all()
    return pedidos
