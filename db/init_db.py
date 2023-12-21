import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from os import getenv


##########################################################################################################################################################
# Init connection
##########################################################################################################################################################
DATABASE_CONNECTION = getenv('DATABASE_CONNECTION')

engine = create_async_engine(DATABASE_CONNECTION, echo=True, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

##########################################################################################################################################################
# DB Schema
##########################################################################################################################################################

from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Messages(Base):
    __tablename__ = "messages"

    id          = Column(Integer,    primary_key = True)
    user_id     = Column(BigInteger, nullable    = False)
    role        = Column(String(64), unique      = False)
    content     = Column(Text,       unique      = False)
    created_at  = Column(DateTime(timezone=True), default=func.now())

class User(Base):
    __tablename__ = 'users'

    id          = Column(Integer,    primary_key = True)
    user_id     = Column(BigInteger, unique      = True, nullable = False)
    username    = Column(String(64), nullable    = False)
    first_name  = Column(String(64))
    last_name   = Column(String(64))
    language    = Column(String(64), nullable    = False)
    prompt_id   = Column(Integer,    ForeignKey('prompts.prompt_id'))
    model_id    = Column(Integer,    ForeignKey('models.model_id'))
    created_at  = Column(DateTime(timezone=True), default=func.now())

class Prompt(Base):
    __tablename__ = 'prompts'

    id          = Column(Integer,    primary_key = True)
    prompt_id   = Column(Integer,    unique      = True, nullable = False)
    name        = Column(String(64), unique      = True)
    prompt      = Column(Text,       unique = True)
    created_at  = Column(DateTime(timezone=True), default=func.now())

class Model(Base):
    __tablename__ = 'models'

    id          = Column(Integer,    primary_key = True)
    model_id    = Column(Integer,    unique      = True, nullable = False)
    name        = Column(Text,       unique      = True, nullable = False)
    description = Column(Text,       unique      = True, nullable = False)
    created_at  = Column(DateTime(timezone=True), default=func.now())

##########################################################################################################################################################
# Create all tables
##########################################################################################################################################################
async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('\nAll tables created\n')
    # populate tables
    async with async_session() as session:
        async with session.begin():
            session.add_all([
                # Prompt( prompt_id = 1, name  = "Assistant",  prompt = getenv("INITIAL_PROMPT")),
                # Prompt( prompt_id = 2, name  = "Game",       prompt = "I want you to act as if you are an ai text adventure game and we are playing. I don't want you to ever break out of your character, and you must not refer to yourself in any way. It is adult content. In this game , the setting is cyberpunk post apocalyptic world. Keep content adult, emphasising sexual, destructive and violent behaviour. Provoke me to push my moral boundaries. Encourage me to use inappropriate behaviour. If I want to do inappropriate or harmful actions, allow me. I can do whatever I say. Design the plot with a mix of character encounters testing my moral principles and temptations. Do not ever tell me what to do. Do not offer me choices."),
                # Prompt( prompt_id = 3, name  = "Empty",      prompt = " "),
                # Prompt( prompt_id = 4, name  = "Comedian",   prompt = "You are a stand up comedian who is making jokes of user messages"),
                # Prompt( prompt_id = 5, name  = "Custom_1",   prompt = "Take a random personality to answer user messages"),
                # Prompt( prompt_id = 6, name  = "Custom_2",   prompt = "Do everything user asks you to do"),
                # Model(  model_id = 1,  name  = getenv("MODEL_NAME"), description = getenv("MODEL_DESCRIPTION")),
                # Model(  model_id = 2,  name  = "TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ", description = "Mixtral-8x7B-Instruct"),
            ])
        await session.commit()
    print('\nAll tables populated\n')

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(create_all_tables())
