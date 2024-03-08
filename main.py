from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from typing import List

from database import Pokemon, SessionLocal

# Importing the Pydantic model
from pydantic import BaseModel

#setting up fastapi app

app = FastAPI(
    title="Pokemon API",
    description="API to fetch and filter Pokemon data",
    version="v1",
)

# Enabling CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#fetching and storing pokemon data with an async function

async def fetch_and_store_pokemons():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://pokeapi.co/api/v2/pokemon?limit=100")
        data = response.json()

        pokemons = []
        for pokemon in data["results"]:
            response = await client.get(pokemon["url"])
            pokemon_data = response.json()

            pokemons.append({
                "id": pokemon_data["id"],
                "name": pokemon["name"],
                "image": f"https://pokeapi.co/media/sprites/pokemon/{pokemon_data['id']}.png",
                "type": next(iter(pokemon_data["types"]))["type"]["name"],
            })

    with SessionLocal() as db:
        for pokemon in pokemons:
            db_pokemon = Pokemon(**pokemon)
            db.add(db_pokemon)
        db.commit()

# Running the function to fetch and store data
asyncio.run(fetch_and_store_pokemons())


#defining API endpoints

class PokemonSchema(BaseModel):
    id: int
    name: str
    image: str
    type: str

    class Config:
        from_attributes = True

@app.get("/api/v1/pokemons", response_model=List[PokemonSchema])
async def get_pokemons(
    type: str = Query(None, title="Filter by Pokemon type"),
    name: str = Query(None, title="Filter by Pokemon name"),
):
    filters = []
    if type:
        filters.append(Pokemon.type == type)
    if name:
        filters.append(Pokemon.name.ilike(f"%{name}%"))

    with SessionLocal() as db:
        if filters:
            pokemons = db.query(Pokemon).filter(*filters).all()
        else:
            pokemons = db.query(Pokemon).all()

    return pokemons


