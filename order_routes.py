from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import PedidoSchema
from models import Pedido

order_router = APIRouter(prefix='/pedidos', tags=['pedidos'])

@order_router.get('/')
async def pedidos():
    return {'mensagem':'voce acessou a rota de pedidos'}

@order_router.post('/pedidos')
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario=pedido_schema.usuario)
    session.add(novo_pedido)
    session.commit()
    return {'mensagem': f'Pedido criado com sucesso. ID do Pedido: {novo_pedido.id}'}