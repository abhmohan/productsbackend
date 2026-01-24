from fastapi import FastAPI
from models import Product
import pymongo
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from fastapi.middleware.cors import CORSMiddleware

connectionString = "mongodb+srv://abhijitmohanty92_db_user:xLdpHzn1vlpd8CrA@cluster0.upkkitj.mongodb.net/"

client = pymongo.MongoClient(connectionString)

db = client["products-db"]
collection = db["products-collection"]


class Item(BaseModel):
    name: str
    price: float
    quantity: int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def serialize(doc):
    return {
        "id": str(doc["_id"]),
        **{k: v for k, v in doc.items() if k != "_id"}
    }

@app.get("/")
def greet():
    return "Hello, World!"


@app.post('/products')
def create_item(item: Item):
    result = collection.insert_one(item.dict())
    return {"id": str(result.inserted_id), **item.dict()}

@app.get('/products')
def get_products():


    # product_id = collection.insert_one({ "name": "Engul" }).inserted_id

    products = list(collection.find())
    return [serialize(p) for p in products]
