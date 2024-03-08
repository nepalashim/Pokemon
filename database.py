import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://shashinoorghimire@localhost/pokemon_db"

try:
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata = sqlalchemy.MetaData()
except SQLAlchemyError as e:
    print(f"An error occurred while creating the engine or metadata: {e}")


#Here I have defined the database model
Base = declarative_base()

class Pokemon(Base):
    __tablename__ = "pokemons"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, index=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    type = sqlalchemy.Column(sqlalchemy.String)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)