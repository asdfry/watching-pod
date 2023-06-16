from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.database_handler import dh

watchers = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db_watcher import DatabaseWatcher
    from app.pod_watcher import PodWatcher

    watchers["db"] = DatabaseWatcher()  # Init and start database watcher
    watchers["pod"] = PodWatcher()  # Init pod watcher
    watchers["pod"].start()  # Start pod watcher
    yield
    watchers["pod"].stop()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Healch Check", "db": dh.health_check()},
    )


@app.get("/services")
def get_services():
    status_code, msg, data = dh.get_items()
    return JSONResponse(
        status_code=status_code,
        content={"message": msg, "data": data},
    )


@app.delete("/services/{namespace}/{name}")
def delete_services(name, namespace):
    status_code, msg = dh.delete_item(name, namespace)
    return JSONResponse(
        status_code=status_code,
        content={"message": msg},
    )
