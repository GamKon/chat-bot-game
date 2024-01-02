# from os import getenv
# import asyncpg
# from db.db_schema import User, Message
# from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
#from db.init_db import db_url
from sqlalchemy import select
from sqlalchemy.sql.expression import Delete, Update
from sqlalchemy.dialects.postgresql import insert

from db.init_db import engine, User, Message, Prompt, Model
#engine = create_async_engine(db_url, echo=True, future=True)
# # async_sessionmaker: a factory for new AsyncSession objects.
# # expire_on_commit - don't expire objects after transaction commit
#async_session = async_sessionmaker(engine, expire_on_commit=False)

##########################################################################################################################################################
# select prompt and model for user
async def select_user_settings(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select( Prompt.name,
                                            Model.description,
                                            Prompt.prompt,
                                            Prompt.user_role_name,
                                            Prompt.ai_role_name,
                                            User.chat_id).where(
                                               Prompt.user_id   == user_id,
                                               Prompt.id        == User.prompt_id,
                                               Model.model_id   == User.model_id,
                                               User.user_id     == user_id
                                            ))
    return result.first()

##########################################################################################################################################################
# Add user
async def add_user(user_id, first_name, last_name, username, language, model_id, chat_id):
    async with engine.begin() as conn:
        await conn.execute(insert(User).values(
                user_id     = user_id,
                first_name  = first_name,
                last_name   = last_name,
                username    = username,
                language    = language,
                model_id    = model_id,
                chat_id     = chat_id
            ).on_conflict_do_nothing(index_elements=['user_id']))
##########################################################################################################################################################
# Select 1 user
async def show_user(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(User).where(User.user_id == user_id))
    return result.first()
##########################################################################################################################################################
# Show user status
async def user_status(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(
            User.user_id,
            User.username,
            User.first_name,
            User.last_name,
            User.language,
            Model.description,
            Prompt.prompt,
            User.chat_id).where(
                User.user_id == user_id,
                Prompt.id == User.prompt_id,
                Prompt.user_id == User.user_id,
                User.model_id == Model.model_id))
    return result.first()
##########################################################################################################################################################
# Get all user messages
async def select_user_chat_history(user_id):
    async with engine.begin() as conn:
        current_chat_id = await conn.execute(select(User.chat_id).where(User.user_id == user_id)).first()
        result = await conn.execute(select(Message.author, Message.content).where(Message.user_id == user_id, Message.chat_id == current_chat_id[0]).order_by(Message.id.asc()))
        return result.all()
##########################################################################################################################################################
# Add user message
async def add_message(user_id, author, content):
    async with engine.begin() as conn:
        current_chat_id = await conn.execute(select(User.chat_id).where(User.user_id == user_id)).first()
        await conn.execute(insert(Message).values(
                user_id     = user_id,
                author      = author,
                content     = content,
                chat_id    = current_chat_id[0]
            ))
##########################################################################################################################################################
# Select last User question
async def select_last_question(user_id):
    async with engine.begin() as conn:
        current_chat_id = await conn.execute(select(User.chat_id).where(User.user_id == user_id)).first()
        result = await conn.execute(select(Message.content).where(Message.user_id == user_id, Message.author == "user", Message.chat_id == current_chat_id[0]).order_by(Message.id.desc()))
    return result.first()
##########################################################################################################################################################
# Delete last user message
async def delete_last_message(user_id):
    async with engine.begin() as conn:
        current_chat_id = await conn.execute(select(User.chat_id).where(User.user_id == user_id)).first()
        last_message = await conn.execute(select(Message.id).where(Message.user_id == user_id, Message.chat_id == current_chat_id[0]).order_by(Message.id.desc()))
        await conn.execute(Delete(Message).where(Message.id == last_message.first()[0]))
##########################################################################################################################################################
# Delete all user messages
async def delete_all_messages(user_id):
    async with engine.begin() as conn:
        current_chat_id = await conn.execute(select(User.chat_id).where(User.user_id == user_id)).first()
        await conn.execute(Delete(Message).where(Message.user_id == user_id, Message.chat_id == current_chat_id[0]))
##########################################################################################################################################################
# Delete last two eser messages
async def delete_last_two_messages(user_id):
    async with engine.begin() as conn:
        current_chat_id = await conn.execute(select(User.chat_id).where(User.user_id == user_id)).first()
        last_message = await conn.execute(select(Message.id).where(Message.user_id == user_id, Message.chat_id == current_chat_id[0]).order_by(Message.id.desc()))
        await conn.execute(Delete(Message).where(Message.id == last_message.first()[0]))
        last_message = await conn.execute(select(Message.id).where(Message.user_id == user_id, Message.chat_id == current_chat_id[0]).order_by(Message.id.desc()))
        await conn.execute(Delete(Message).where(Message.id == last_message.first()[0]))

##########################################################################################################################################################
# Select current initial prompt
async def select_system_prompt(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(
            Prompt.prompt,
            Prompt.user_role_name,
            Prompt.ai_role_name,
            Prompt.id,
            Prompt.name,
            Prompt.max_new_tokens).where(
                Prompt.id == User.prompt_id,
                User.user_id == user_id)
            )
    return result.first()
##########################################################################################################################################################
# Select all prompts
async def select_all_system_prompts(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(
            Prompt.name,
            Prompt.prompt,
            Prompt.id,
            Prompt.max_new_tokens).where(
                Prompt.user_id == user_id).order_by(Prompt.id.asc())
            )
    return result.all()
##########################################################################################################################################################
# update_user_ai_persona
async def update_user_ai_persona(user_id, prompt_id):
    async with engine.begin() as conn:
        await conn.execute(Update(User).where(User.user_id == user_id).values(prompt_id = prompt_id))
##########################################################################################################################################################
# update_user_system_prompt
async def edit_system_prompt(user_id, prompt_text, user_role_name, ai_role_name, save_name, max_new_tokens):
    new_prompt = str(prompt_text)
    if len(new_prompt) < 1024:
        async with engine.begin() as conn:
            await conn.execute(Update(Prompt).where(
                Prompt.id == User.prompt_id,
                User.user_id == user_id).values(
                    prompt = str(prompt_text),
                    user_role_name = user_role_name,
                    ai_role_name = ai_role_name,
                    name = save_name,
                    max_new_tokens = max_new_tokens
                )
            )

##########################################################################################################################################################
# Select User chat_id
async def select_user_chat_id(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(User.chat_id).where(User.user_id == user_id))
    return result.first()
##########################################################################################################################################################
# update_user_ai_persona
async def update_user_chat(user_id, chat_id):
    async with engine.begin() as conn:
        await conn.execute(Update(User).where(User.user_id == user_id).values(chat_id = chat_id))

##########################################################################################################################################################
# Select all models
async def select_all_models():
    async with engine.begin() as conn:
        result = await conn.execute(select(
            Model.name,
            Model.description,
            Model.model_id).order_by(
                Model.model_id.asc()))
    return result.all()
##########################################################################################################################################################
async def update_user_llm_model(user_id, model_id):
    async with engine.begin() as conn:
        await conn.execute(Update(User).where(User.user_id == user_id).values(model_id = model_id))
##########################################################################################################################################################
async def select_user_llm_model(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(
            Model.name,
            Model.model_id,
            Model.prompt_format).where(User.user_id == user_id,
                                       Model.model_id == User.model_id
                                       )
            )
    return result.first()
##########################################################################################################################################################


##########################################################################################################################################################
# Add default_user prompts
##########################################################################################################################################################
async def add_default_user_prompts(user_id):
    async with engine.begin() as conn:

        # Select default prompts (where user_id == None )
        default_prompts = await conn.execute(select(
            Prompt.id,
            Prompt.name,
            Prompt.prompt,
            Prompt.user_role_name,
            Prompt.ai_role_name,
            Prompt.max_new_tokens).where(
                Prompt.user_id == None))
        print("default_prompts")
        default_prompts = default_prompts.all()

        # Fill out the list of prompts with user_id before adding them back to the DB
        for prompt in default_prompts:
            print(prompt[1])
            await conn.execute(insert(Prompt).values(
                    user_id         = user_id,
                    name            = prompt[1],
                    prompt          = prompt[2],
                    user_role_name  = prompt[3],
                    ai_role_name    = prompt[4],
                    max_new_tokens  = prompt[5]
                ))#.on_conflict_do_nothing(index_elements=['prompt_id']))
        personal_prompts = await conn.execute(select(Prompt.id).where(Prompt.user_id == user_id).order_by(Prompt.id.asc()))
        personal_prompts = personal_prompts.all()
        # Assign second personal prompt to user
        print(personal_prompts)
        try:
            await conn.execute(Update(User).where(User.user_id == user_id).values(prompt_id = personal_prompts[1][0]))
        except:
            print("User has no prompts")

##########################################################################################################################################################
