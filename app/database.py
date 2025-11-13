from sqlalchemy import create_engine, MetaData

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker

# 🔗 URL de conexión a PostgreSQL

#SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Olimpia.2025@localhost:5432/postgres"

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:Olimpia.2025@localhost:5432/postgres"

# ⚙️ Crear el motor de conexión

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 🧩 Crear la sesión

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🏗️ Declarative base (usa el esquema "mkt" por defecto)

Base = declarative_base(metadata=MetaData(schema="mkt"))

# 🔁 Dependencia para inyección de sesión en FastAPI

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()
 