import os, jwt, json, string, secrets, functools

from starlette.responses import RedirectResponse

from sqlalchemy import and_, true
from sqlalchemy.future import select

from db_config.settings import settings
from db_config.storage_config import engine, async_session

from account.models import User

from .models import Privileged


key = settings.SECRET_KEY
algorithm = settings.JWT_ALGORITHM
EMAIL_TOKEN_EXPIRY_MINUTES = settings.EMAIL_TOKEN_EXPIRY_MINUTES


async def token_privileged(request, session, model):
    token = request.cookies.get("privileged")
    if token:
        payload = jwt.decode(request.cookies.get("privileged"), key, algorithm)
        prv_key = payload["prv_key"]
        stmt = await session.execute(
            select(Privileged)
            .where(Privileged.prv_key == prv_key)
        )
        prv = stmt.scalars().first()
        stmt = await session.execute(
            select(User).where(and_(User.id == prv.prv_in, User.privileged, true()))
        )
        prv = stmt.scalars().first()
        stmt = await session.execute(
            select(model).where(model.owner == prv.id)
        )
        result = stmt.scalars().all()
        return result


# ...
async def get_token_privileged(request):
    while True:
        if not request.cookies.get("privileged"):
            break
        if request.cookies.get("privileged"):
            payload = None
            try:
                payload = jwt.decode(request.cookies.get("privileged"), key, algorithm)
            except jwt.exceptions.InvalidTokenError:
                break
            prv_key = payload["prv_key"]
            return prv_key

async def get_privileged(request, session):
    while True:
        token = await get_token_privileged(request)
        if not token:
            break
        if token:
            stmt = await session.execute(
                select(Privileged)
                .where(Privileged.prv_key == token)
            )
            result = stmt.scalars().first()
            return result

async def get_privileged_user(request, session):
    while True:
        prv = await get_privileged(request, session)
        if not prv:
            break
        if prv:
            stmt = await session.execute(
                select(User).where(and_(User.id == prv.prv_in, User.privileged, true()))
            )
            result = stmt.scalars().first()
            return result

async def get_owner_prv(request, session, model):
    while True:
        prv = await get_privileged_user(request, session)
        if not prv:
            break
        if prv:
            stmt = await session.execute(
                select(model).where(model.owner == prv.id)
            )
            result = stmt.scalars().all()
            return result


def privileged():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *a, **ka):
            async with async_session() as session:
                user = await get_privileged_user(request, session)
            await engine.dispose()
            if user:
                return await func(request, *a, **ka)
            return RedirectResponse("/privileged/login")
        return wrapper
    return decorator
# ...


async def id_and_owner_prv(request, session, model, id):
    prv = await get_privileged_user(request, session)
    stmt = await session.execute(
        select(model).where(
            and_(
                model.id == id,
                model.owner == prv.id,
            )
        )
    )
    result = stmt.scalars().first()
    return result


async def owner_prv(session, model, prv):
    stmt = await session.execute(
        select(model).where(model.owner == prv.id)
    )
    result = stmt.scalars().all()
    return result


# ..
async def get_random_string():
    alphabet = string.ascii_letters + string.digits
    prv_key = "".join(secrets.choice(alphabet) for i in range(32))
    return prv_key
