from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config_reader import config

DATABASE_URL = f"postgresql+asyncpg://{config.db.user.get_secret_value()}:" \
               f"{config.db.password.get_secret_value()}" \
               f"@{config.db.host.get_secret_value()}" \
               f":{config.db.port.get_secret_value()}" \
               f"/{config.db.db.get_secret_value()}"

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
