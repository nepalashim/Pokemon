from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import List


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
    # Use httpx to fetch data from PokeAPI
    async with httpx.AsyncClient() as client:
        response = await client.get("https://pokeapi.co/api/v2/pokemon?limit=100")

    # Extraction of relevant data from the response
    pokemons = [
        {
            "name": pokemon["name"],
            "image": f"https://pokeapi.co/media/sprites/pokemon/{pokemon['url'].split('/')[-2]}.png",
            "type": next(iter(pokemon["types"]))["type"]["name"],
        }
        for pokemon in response.json()["results"]
    ]

    # Storation of data in the database
    async with SessionLocal() as db:
        for pokemon in pokemons:
            db_pokemon = Pokemon(**pokemon)
            db.add(db_pokemon)
        db.commit()

# Running the function to fetch and store data
asyncio.run(fetch_and_store_pokemons())


#defining API endpoints

@app.get("/api/v1/pokemons", response_model=List[Pokemon])
async def get_pokemons(
    type: str = Query(None, title="Filter by Pokemon type"),
    name: str = Query(None, title="Filter by Pokemon name"),
):
    # Query the database based on provided filters
    filters = []
    if type:
        filters.append(Pokemon.type == type)
    if name:
        filters.append(Pokemon.name.ilike(f"%{name}%"))

    async with SessionLocal() as db:
        if filters:
            pokemons = db.query(Pokemon).filter(*filters).all()
        else:
            pokemons = db.query(Pokemon).all()

    return pokemons


