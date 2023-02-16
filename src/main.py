"""API Endpoints."""

import io
import json
import logging
import typing

from tqdm import tqdm

from fastapi import FastAPI
from fastapi import responses
from fastapi.middleware.cors import CORSMiddleware

from redis import Redis

import models.product
import models.request


app: FastAPI
origins: typing.List[str]

app = FastAPI()
origins = ["*"]
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
cache = Redis(
    host="redis",
    port=6379,
    db=0,
)


@app.on_event("startup")
async def set_product_cache() -> None:
    key: str
    line: str
    row: dict
    dbsize: int
    file_path: str
    reader: io.TextIOWrapper

    dbsize = cache.dbsize()
    if dbsize > 0:
        return

    logging.info("Caching products.")
    pipeline = cache.pipeline()
    file_path = "/data/products.json"
    with open(file=file_path, mode="r") as reader:
        for line in tqdm(reader.readlines()):
            row = json.loads(line)
            key = "product_" + str(row["id_product"])
            pipeline.json().set(key, "$", row)
    pipeline.execute()


@app.get("/")
def read_root() -> responses.HTMLResponse:
    """Get backend main page."""
    image: str
    content: str
    file_path: str
    reader: io.TextIOWrapper
    response: responses.HTMLResponse

    file_path = "/app/public/index.html"
    with open(file=file_path, mode="r") as reader:
        content = reader.read()

    file_path = "/app/public/logo.txt"
    with open(file=file_path, mode="r") as reader:
        content = content.replace("__logo__", reader.read())

    response = responses.HTMLResponse(
        content=content,
        status_code=200,
    )
    return response


@app.post("/product")
def get_product(request: models.request.Request) -> responses.JSONResponse:
    key: str
    product: models.product.Product
    content: typing.Dict[str, str]
    response: responses.JSONResponse

    key = cache.randomkey().decode("utf-8")
    content = cache.json().get(name=key)
    product = models.product.Product(
        name=content["name"],
        description=content["description"],
        image_url=content["image_url"],
    )
    product.process()
    content = product.dict()

    response = responses.JSONResponse(
        content=content,
        status_code=200,
    )
    return response
