from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dependencies import pegar_sessao, verificar_token
from app.models import Usuario
from app.schemas import UsuarioSchema, LoginSchema
from app.security import (
    bcrypt_context,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def criar_token(
    id_usuario,
    duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
):
    data_expiracao = datetime.now(timezone.utc) + duracao_token

    dados = {
        "user_id": str(id_usuario),
        "exp": data_expiracao,
    }

    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)


def autenticar_usuario(email, senha, session):
    usuario = session.scalar(select(Usuario).where(Usuario.email == email))

    if not usuario:
        return False

    if not bcrypt_context.verify(senha, usuario.senha):
        return False

    return usuario


@auth_router.get("/")
async def home():
    return {
        "mensagem": "voce acessou a rota padrao de autenticaçao",
        "autenticado": False,
    }


@auth_router.post("/criar_conta")
async def criar_conta(
    usuario_schema: UsuarioSchema,
    session: Session = Depends(pegar_sessao),
):
    usuario = session.scalar(
        select(Usuario).where(Usuario.email == usuario_schema.email)
    )

    if usuario:
        raise HTTPException(
            status_code=400,
            detail="E-mail do usuário já cadastrado",
        )

    senha_criptografada = bcrypt_context.hash(usuario_schema.senha)

    novo_usuario = Usuario(
        nome=usuario_schema.nome,
        email=usuario_schema.email,
        senha=senha_criptografada,
        ativo=usuario_schema.ativo,
        admin=usuario_schema.admin,
    )

    session.add(novo_usuario)
    session.commit()

    return {"mensagem": f"usuário cadastrado com sucesso {usuario_schema.email}"}


@auth_router.post("/login")
async def login(
    login_schema: LoginSchema,
    session: Session = Depends(pegar_sessao),
):
    usuario = autenticar_usuario(
        login_schema.email,
        login_schema.senha,
        session,
    )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="Usuário não encontrado ou credenciais inválidas",
        )

    access_token = criar_token(usuario.id)
    refresh_token = criar_token(
        usuario.id,
        duracao_token=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


@auth_router.post("/login-form")
async def login_form(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(pegar_sessao),
):
    usuario = autenticar_usuario(
        dados_formulario.username,
        dados_formulario.password,
        session,
    )

    if not usuario:
        raise HTTPException(
            status_code=400,
            detail="Usuário não encontrado ou credenciais inválidas",
        )

    access_token = criar_token(usuario.id)
    refresh_token = criar_token(
        usuario.id,
        duracao_token=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }
