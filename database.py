#here i ve defined the database models

Base = declarative_base()

class Pokemon(Base):
    __tablename__ = "pokemons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image = Column(String)
    type = Column(String)


#here i ve created a database connection function

DATABASE_URL = "postgresql+asyncpg://username:password@localhost/pokemon_db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Create the database tables
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
