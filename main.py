from fastapi import FastAPI
from schemas.schemas import Subscription


# Caso precise instanciar o FastAPI
app = FastAPI()

# TODO inserir no router
@app.post("/libraries/subscribe/")
async def create_subscription(subscription:Subscription):
    return {
        "message": "Dados recebidos com sucesso",
        "tags": subscription.tags,
        "libraries_list": subscription.libraries_list
    }