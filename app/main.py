from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

handlers = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database_handler import dh
    from app.kubernetes_handler import KubernetesHandler

    handlers["db"] = dh  # Get DB handler
    handlers["k8s"] = KubernetesHandler()  # Init Kubernetes handler
    handlers["k8s"].start()
    yield
    handlers["k8s"].stop()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Healch Check", "db": handlers["db"].health_check()},
    )


@app.get("/services")
def get_services():
    status_code, data = handlers["db"].get_items()
    return JSONResponse(
        status_code=status_code,
        content={"message": "Get Services", "data": data},
    )


@app.delete("/services/{namespace}/{name}")
def delete_services(name, namespace):
    status_code = handlers["k8s"].delete_service(name, namespace)
    if status_code == 200:
        status_code = handlers["db"].delete_item(name, namespace)
    return JSONResponse(
        status_code=status_code,
        content={"message": "Delete Services"},
    )
