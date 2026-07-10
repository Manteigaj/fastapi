from typing import List

from pydantic import BaseModel, ConfigDict


class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str
    ativo: bool = True
    admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class PedidoSchema(BaseModel):
    usuario: int

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    email: str
    senha: str

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoSchema(BaseModel):
    quantidade: int
    sabor: str
    tamanho: str
    preco_unitario: float

    model_config = ConfigDict(from_attributes=True)


class ResponsePedidoSchema(BaseModel):
    id: int
    status: str
    preco: float
    itens: List[ItemPedidoSchema]

    model_config = ConfigDict(from_attributes=True)
