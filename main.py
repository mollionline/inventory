from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host='redis-15731.c295.ap-southeast-1-1.ec2.redns.redis-cloud.com',
    port=15731,
    password='olfvcIqnwFINwdOHAHneN34Z0Iwel0fh',
    decode_responses=True
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


@app.post('/products')
def create(product: dict):
    try:
        product = Product.parse_obj(product)
        return product.save()
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())


@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)


@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)
