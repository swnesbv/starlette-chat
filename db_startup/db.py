from __future__ import annotations

from datetime import datetime

import string
import secrets
import time
import bcrypt

from collocutor.models import PersonCollocutor
from participant.models import PersonParticipant
from channel.models import GroupChat, MessageGroup, OneOneChat

from account.models import User
from auth_privileged.models import Privileged

from db_config.storage_config import Base, engine, async_session


def get_random_string():
    alphabet = string.ascii_letters + string.digits
    prv_key = "".join(secrets.choice(alphabet) for i in range(32))
    return prv_key


async def on_app_startup() -> None:
    async with engine.begin() as conn:
        # ..
        start = time.time()
        print(" start..")
        # ..
        await conn.run_sync(Base.metadata.create_all)
        # ..
        end = time.time()
        print(" end..", end - start)

    async with async_session() as session:
        async with session.begin():
            # ..
            hashed_password = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt())
            password_hash = hashed_password.decode('utf8')
            # ..
            start = time.time()
            print(" start add_all..")
            # ..
            session.add_all(
                [
                    User(
                        name="one",
                        email="one@example.com",
                        password=password_hash,
                        is_admin=True,
                        is_active=True,
                        privileged=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    User(
                        name="two",
                        email="two@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        privileged=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    User(
                        name="three",
                        email="three@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    User(
                        name="four",
                        email="four@example.com",
                        password=password_hash,
                        is_admin=False,
                        is_active=True,
                        email_verified=True,
                        created_at=datetime.now(),
                    ),
                    Privileged(
                        prv_key=get_random_string(),
                        prv_in=1,
                    ),
                    GroupChat(
                        title="chat group (one)",
                        description="description group (one) owner: one@example.com",
                        owner=1,
                        created_at=datetime.now(),
                    ),
                    MessageGroup(
                        message="message",
                        owner=1,
                        id_group=1,
                        created_at=datetime.now(),
                    ),
                    PersonParticipant(
                        explanatory_note="gr-1 admin - note",
                        permission=1,
                        owner=1,
                        community=1,
                        created_at=datetime.now(),
                    ),
                    PersonParticipant(
                        explanatory_note="gr-1 three - note",
                        permission=0,
                        owner=3,
                        community=1,
                        created_at=datetime.now(),
                    ),
                    PersonCollocutor(
                        ref_num="1-2",
                        explanatory_note="note..1+2",
                        permission=1,
                        owner=1,
                        community=2,
                        created_at=datetime.now(),
                    ),
                    PersonCollocutor(
                        explanatory_note="note..2+3",
                        permission=0,
                        owner=2,
                        community=3,
                        created_at=datetime.now(),
                    ),
                    PersonCollocutor(
                        explanatory_note="note..4+3",
                        permission=0,
                        owner=4,
                        community=3,
                        created_at=datetime.now(),
                    ),
                    OneOneChat(
                        message="OneOneChat message",
                        owner=1,
                        one_one=1,
                        created_at=datetime.now(),
                    ),
                ]
            )
            await session.flush()
        await session.commit()
        end = time.time()
        print(" end add_all..", end - start)
    await engine.dispose()


async def on_app_shutdown() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
