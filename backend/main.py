from fastapi import FastAPI
from models import Product
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from bson.errors import InvalidId


from fastapi.middleware.cors import CORSMiddleware

connectionString = "mongodb+srv://abhijitmohanty92_db_user:xLdpHzn1vlpd8CrA@cluster0.upkkitj.mongodb.net/"

client = MongoClient(connectionString)

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
        **{ k: v for k, v in doc.items() if k != "_id" }
    }

@app.get("/")
def greet():
    return "Hello, World!"


@app.post('/products')
def create_item(item: Item):
    result = collection.insert_one(item.dict())
    return { "id": str(result.inserted_id), **item.dict() }

@app.get('/products')
def get_products():
    products = list(collection.find())
    return [serialize(p) for p in products]
    
@app.put('/products/{product_id}')
def update_product(product_id: str, item: Item):
    result = collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": item.dict()}
    )

    if result.matched_count == 0:
        return {"error": "Product not found"}
    return { "id": product_id, **item.dict() }

@app.delete('/products/{product_id}')
def delete_product(product_id: str):
    try:
        obj_id = ObjectId(product_id)
    except InvalidId:
        return {"error": "Invalid product id"}

    result = collection.delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        return {"error": "Product not found"}

    return {"message": "Product deleted successfully", "id": product_id}

@app.get('/health')
def health_check():
    return { "status": "healthy" }