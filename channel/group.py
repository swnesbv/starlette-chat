from datetime import datetime
import os

from sqlalchemy import insert, update as sqlalchemy_update, delete

from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse, PlainTextResponse

from cryptography.fernet import Fernet

from account.opt_slc import auth

from db_config.storage_config import engine, async_session

from options_select.opt_slc import for_in, left_right_all, for_id, id_and_owner

from auth_privileged.opt_slc import get_privileged_user

from participant.models import PersonParticipant

from .models import MessageGroup, GroupChat
from .opt_slc import in_obj_participant, in_obj_accepted


templates = Jinja2Templates(directory="templates")


async def group_create(request):
    # ..
    template = "/group/create.html"
    # ..
    async with async_session() as session:
        # ...
        if request.method == "GET":
            if request["user"].is_authenticated or request["prv"].is_authenticated:
                return templates.TemplateResponse(
                    template, {"request": request},
                )
            return RedirectResponse("/account/login", status_code=302)
        # ...
        if request.method == "POST":
            # ..
            owner = int
            if request["user"].is_authenticated:
                owner = request.user.user_id
            if request["prv"].is_authenticated:
                owner = await get_privileged_user(request, session)
            # ..
            form = await request.form()
            # ..
            title = form["title"]
            description = form["description"]
            # ..
            new = GroupChat()
            new.title = title
            new.description = description
            new.created_at = datetime.now()
            new.owner = owner.id
            session.add(new)
            await session.commit()
            # ..
            save_path = f"./static/group/{new.id}/"
            os.makedirs(save_path, exist_ok=True)
            # ..
            key = Fernet.generate_key()
            with open(f"{save_path}" + "key.txt", "w", encoding="utf-8") as file:
                file.write(key.decode("utf8"))
            # ..
            p = PersonParticipant()
            p.permission = True
            p.created_at = datetime.now()
            p.owner = owner.id
            p.community = new.id
            session.add(p)
            await session.commit()
            # ..
            f = Fernet(key)
            first_message = f.encrypt(
                f"New message admin group-{owner.email}..!".encode("utf-8")
            )
            query = insert(MessageGroup).values(
                owner=owner.id,
                id_group=new.id,
                message=first_message.decode("utf8"),
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/chat/group/{ new.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


async def group_update(request):
    # ..
    id = request.path_params["id"]
    template = "/group/update.html"
    # ..
    async with async_session() as session:
        owner = int
        if request["user"].is_authenticated:
            owner = request.user.user_id
        if request["prv"].is_authenticated:
            owner = await get_privileged_user(request, session)
        # ..
        detail = await id_and_owner(session, GroupChat, owner, id)
        context = {
            "request": request,
            "detail": detail,
        }
        # ...
        if request.method == "GET":
            if detail:
                return templates.TemplateResponse(template, context)
            return PlainTextResponse("You are banned - this is not your account..!")
        # ...
        if request.method == "POST":
            # ..
            form = await request.form()
            # ..
            detail.title = form["title"]
            detail.description = form["description"]
            # ..
            query = (
                sqlalchemy_update(GroupChat)
                .where(GroupChat.id == id)
                .values(form)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                f"/chat/group/{ detail.id }",
                status_code=302,
            )
            return response
    await engine.dispose()


async def group_delete(request):
    # ..
    id = request.path_params["id"]
    template = "/group/delete.html"
    # ..
    async with async_session() as session:
        # ...
        if request.method == "GET":
            # ..
            owner = int
            i = None
            if request["user"].is_authenticated:
                owner = request.user.user_id
                i = await id_and_owner(session, GroupChat, owner.id, id)
            if request["prv"].is_authenticated:
                owner = await get_privileged_user(request, session)
                i = await id_and_owner(session, GroupChat, owner.id, id)
            # ..
            if i:
                return templates.TemplateResponse(
                    template,
                    {
                        "request": request,
                        "i": i,
                    },
                )
            return PlainTextResponse("this is not your group..!")
        # ...
        if request.method == "POST":
            # ..
            query = delete(GroupChat).where(GroupChat.id == id)
            await session.execute(query)
            await session.commit()
            # ..
            response = RedirectResponse(
                "/chat/group/list",
                status_code=302,
            )
            return response
    await engine.dispose()


@auth()
# ..
async def group_details(request):
    # ..
    id = request.path_params["id"]
    template = "/group/details.html"
    # ..
    if request.method == "GET":
        # ..
        async with async_session() as session:
            # ..
            gh = await for_id(session, GroupChat, id)
            # ..
            prv = await get_privileged_user(request, session)
            # ..
            result = await left_right_all(
                session, MessageGroup, MessageGroup.id_group, id
            )
            # ..
            save_path = f"./static/group/{id}/"
            with open(save_path + "key.txt", "r", encoding="utf-8") as key:
                key_read = key.read()
                f = Fernet(key_read.encode("utf-8"))
                group_chat = [
                    {
                        "id": i.id,
                        "message": f.decrypt(i.message).decode("utf-8"),
                        "file": i.file,
                        "created_at": i.created_at,
                        "modified_at": i.modified_at,
                        "owner": i.owner,
                        "id_group": i.id_group,
                    }
                    for i in result
                ]
            # ..
            context = {
                "request": request,
                "i": gh,
                "prv": prv,
                "id_group": id,
                "group_chat": group_chat,
            }
            # ..
            if prv:
                for_prv = await in_obj_participant(session, prv.id, id)
                for_prv_accepted = await in_obj_accepted(session, prv.id, id)
                # ..
                context["for_prv"] = for_prv
                context["for_prv_accepted"] = for_prv_accepted
            # ..
            if request.cookies.get("visited"):
                for_user = await in_obj_participant(session, request.user.user_id, id)
                for_user_accepted = await in_obj_accepted(
                    session, request.user.user_id, id
                )
                # ..
                context["for_user"] = for_user
                context["for_user_accepted"] = for_user_accepted

            return templates.TemplateResponse(template, context)
        await engine.dispose()


async def group_list(request):
    # ..
    template = "/group/list.html"

    async with async_session() as session:
        result = await for_in(session, GroupChat)
        context = {
            "request": request,
            "result": result,
        }

        return templates.TemplateResponse(template, context)
    await engine.dispose()
