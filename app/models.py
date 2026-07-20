from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    pedidos: Mapped[list["Pedido"]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
    )


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDENTE")
    preco: Mapped[float] = mapped_column(Float, default=0)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"),
    )

    usuario: Mapped["Usuario"] = relationship(
        back_populates="pedidos",
    )

    itens: Mapped[list["ItensPedido"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
    )

    def calcular_preco(self) -> None:
        self.preco = sum(item.preco_unitario * item.quantidade for item in self.itens)


class ItensPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quantidade: Mapped[int] = mapped_column(Integer)
    sabor: Mapped[str] = mapped_column(String(100))
    tamanho: Mapped[str] = mapped_column(String(30))
    preco_unitario: Mapped[float] = mapped_column(Float)

    pedido_id: Mapped[int] = mapped_column(
        ForeignKey("pedidos.id"),
    )

    pedido: Mapped["Pedido"] = relationship(
        back_populates="itens",
    )
