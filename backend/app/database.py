from app.config import settings
from sqlmodel import Session, SQLModel, create_engine

db_url = str(settings.DATABASE_URL)
connect_args = {}
engine_kwargs = {}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=settings.DEBUG,
    **engine_kwargs,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session
