import os, jwt, json, string, secrets, functools

from sqlalchemy import and_, or_, not_, true, false
from sqlalchemy.future import select


from participant.models import PersonParticipant


async def person_participant(session, model, obj):
    stmt = await session.execute(
        select(model).where(
            model.owner == obj,
        )
    )
    result = stmt.scalars().first()
    return result


async def all_true(session, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.community == id,
                PersonParticipant.permission,
                true(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def all_false(session, id):
    stmt = await session.execute(
        select(PersonParticipant).where(
            and_(
                PersonParticipant.community == id,
                PersonParticipant.permission == false(),
            )
        )
    )
    result = stmt.scalars().all()
    return result


async def stop_double(session, model, obj, id):
    stmt_admin = await session.execute(
        select(model)
        .where(
            model.community == id,
            model.owner == obj,
        )
    )
    result = stmt_admin.scalars().first()
    return result
