# from os import getenv
# import asyncpg
# from db.db_schema import User, Messages
# from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
#from db.init_db import db_url
from sqlalchemy import select
from sqlalchemy.sql.expression import Delete, Update
from sqlalchemy.dialects.postgresql import insert

from db.init_db import engine, User, Messages, Prompt, Model
#engine = create_async_engine(db_url, echo=True, future=True)
# # async_sessionmaker: a factory for new AsyncSession objects.
# # expire_on_commit - don't expire objects after transaction commit
#async_session = async_sessionmaker(engine, expire_on_commit=False)

##########################################################################################################################################################
# select prompt and model for user
async def select_user_settings(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(Prompt.name, Model.description).where(User.prompt_id == Prompt.id, User.model_id == Model.id, User.user_id == user_id))
    return result.first()

##########################################################################################################################################################
# Add user
async def add_user(user_id, first_name, last_name, username, language, prompt_id, model_id):
    async with engine.begin() as conn:
        await conn.execute(insert(User).values(
                user_id     = user_id,
                first_name  = first_name,
                last_name   = last_name,
                username    = username,
                language    = language,
                prompt_id   = prompt_id,
                model_id    = model_id
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
        result = await conn.execute(select(User.user_id,
                                           User.username,
                                           User.first_name,
                                           User.last_name,
                                           User.language,
                                           Model.description,
                                           Prompt.prompt
                                    ).where(User.user_id == user_id,
                                            User.prompt_id == Prompt.id,
                                            User.model_id == Model.id))
    return result.first()
##########################################################################################################################################################
# Get all user messages
async def select_user_chat_history(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(Messages.role, Messages.content).where(Messages.user_id == user_id).order_by(Messages.id.asc()))
        return result.all()
##########################################################################################################################################################
# Add user message
async def add_message(user_id, role, content):
    async with engine.begin() as conn:
        await conn.execute(insert(Messages).values(
                user_id     = user_id,
                role        = role,
                content     = content,
            ))
##########################################################################################################################################################
# Delete last user message
async def delete_last_message(user_id):
    async with engine.begin() as conn:
        await conn.execute(Delete(Messages).where(Messages.user_id == user_id).order_by(Messages.id.desc()).first())
##########################################################################################################################################################
# Delete all user messages
async def delete_all_messages(user_id):
    async with engine.begin() as conn:
        await conn.execute(Delete(Messages).where(Messages.user_id == user_id))
##########################################################################################################################################################
# Delete last two user messages
async def delete_last_two_messages(user_id):
    async with engine.begin() as conn:
        last_message = await conn.execute(select(Messages).where(Messages.user_id == user_id).order_by(Messages.id.desc()).first())
        await conn.execute(Delete(last_message))


async def delete_row(session, model, primary_key):
    # Get the query object for the row you want to delete
    query = session.query(Messages)
    row_to_delete = await query.filter(Messages.id == primary_key).gino.first()

#     if row_to_delete:
#         # Delete the row
#         await row_to_delete.delete()
#         await session.commit()
#     else:
#         print("Row not found")



##########################################################################################################################################################
# Select current initial prompt
async def select_system_prompt(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(Prompt.prompt).where(Prompt.prompt_id == User.prompt_id, User.user_id == user_id))
    return result.first()
##########################################################################################################################################################
# Select all prompts
async def select_all_system_prompts():
    async with engine.begin() as conn:
        result = await conn.execute(select(Prompt.name, Prompt.prompt, Prompt.prompt_id))
    return result.all()
##########################################################################################################################################################
# update_user_ai_persona
async def update_user_ai_persona(user_id, prompt_id):
    async with engine.begin() as conn:
        await conn.execute(Update(User).where(User.user_id == user_id).values(prompt_id = prompt_id))

##########################################################################################################################################################
# Select all models
async def select_all_models():
    async with engine.begin() as conn:
        result = await conn.execute(select(Model.name, Model.description, Model.model_id))
    return result.all()
##########################################################################################################################################################
async def update_user_llm_model(user_id, model_id):
    async with engine.begin() as conn:
        await conn.execute(Update(User).where(User.user_id == user_id).values(model_id = model_id))
##########################################################################################################################################################
async def select_user_llm_model(user_id):
    async with engine.begin() as conn:
        result = await conn.execute(select(Model.name).where(Model.model_id == User.model_id))#, User.user_id == user_id))
    return result.first()
##########################################################################################################################################################

# async save_tutorial(tutorial: Tutorial) -> Tutorial:
#     async with get_session() as session:
# #        …
#         await session.commit()
# ##        …

# from sqlalchemy import create_engine, select
# from sqlalchemy.orm import sessionmaker, Session

# an Engine, which the Session will use for connection resources
##engine = create_async_engine(db_url)
# a sessionmaker(), also in the same scope as the engine
##async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
##async_session()
# async_session.configure(bind=engine)
# async def add_user(user_id, username):
#     async with async_session(engine) as session:
#         async with async_session.begin():
#             result = await async_session.execute(User.insert().values(
#                 telegram_user_id=user_id,
#                 first_name="123",
#                 last_name="456",
#                 username=username
#             ))
#     return result.all()

    # new_user = User(username=message.from_user.username, fullname=message.from_user.full_name)
    # # Add the new user to the database session
    # Session.add(new_user)
    # # Commit the transaction
    # await trans.commit()





# async def delete_user_chat_history(user_id):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(Messages.delete().where(Messages.c.user_id == user_id))
#             return result.all()

# async def insert_user_chat_history(user_id, message_id, text):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(Messages.insert().values(user_id=user_id, message_id=message_id, text=text))
#             return result.all()

# async def add_user_chat_history(user_id, message_id, text):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(Messages.insert().values(user_id=user_id, message_id=message_id, text=text))
#             return result.all()

# async def remove_last_user_chat_history(user_id):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(Messages.delete().where(Messages.c.user_id == user_id).order_by(Messages.c.message_id.desc()).limit(1))
#             return result.all()

# async def remove_last_chath_history_of_user(user_id):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(Messages.delete().where(Messages.c.user_id == user_id).order_by(Messages.c.message_id.desc()).limit(1))
#             return result.all()

# async def select_first_chat_history_of_user(user_id):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(select(Messages).where(Messages.c.user_id == user_id).order_by(Messages.c.message_id.asc()).limit(1))
#             return result.all()

# async def replace_first_chat_history_of_user(user_id, message_id, text):
#     async with async_session(engine) as session:
#         async with session.begin():
#             result = await session.execute(Messages.update().where(Messages.c.user_id == user_id).order_by(Messages.c.message_id.asc()).limit(1).values(message_id=message_id, text=text))
#             return result.all()

# async def init_new_user(message):
#     await add_user( user_id     = message.from_user.id,
#                     first_name  = message.from_user.first_name,
#                     last_name   = message.from_user.last_name,
#                     username    = message.from_user.username,
#                     language    = "English",
#                     prompt_id   = 1,
#                     model_id    = 1)
#     initial_prompt = await select_initial_prompt(prompt_id = 1)
#     print(f"Initial prompt: \n{initial_prompt}")
#     await add_message(user_id = message.from_user.id, role = "System", content = initial_prompt[0][1])

#     print(f"User: {message.from_user.username} addes to DB")
#     content = Text("Hello, ", Bold(result[0][3]), "!")
