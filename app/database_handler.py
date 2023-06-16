from typing import Dict, Tuple
from fastapi import status
from sqlalchemy.orm import Session

from app.ready import Pod, engine
from app.log_handler import logger


class DatabaseHandler:
    def __init__(self) -> None:
        logger.info("[DB Handler] Init database handler")

    def health_check(self) -> bool:
        with Session(engine) as session:
            try:
                session.connection()
                return True
            except Exception as e:
                logger.error("[DB Handler]", e)
                return False

    def get_items(self) -> Tuple[int, str, list]:
        with Session(engine) as session:
            try:
                # Query all items from the Pod table
                items = session.query(Pod).all()
                pods = [
                    {
                        "name": item.name,
                        "namespace": item.namespace,
                        "labels": item.labels,
                        "targetport": item.targetport,
                    }
                    for item in items
                ]
                logger.info("[DB Handler] Get items success")
                return (status.HTTP_200_OK, "Get Items Success", pods)

            except Exception as e:
                logger.error("[DB Handler]", e)
                logger.error("[DB Handler] Get items fail")
                return (status.HTTP_500_INTERNAL_SERVER_ERROR, "Get Items Fail", [])

    def insert_item(self, name: str, namespace: str, targetport: str, labels: Dict) -> int:
        with Session(engine) as session:
            try:
                # Create item and insert
                item = Pod(name=name, namespace=namespace, targetport=targetport, labels=labels)
                session.add(item)
                session.commit()
                logger.info(f"[DB Handler] Insert item success: name={name}, namespace={namespace}")
                return status.HTTP_200_OK

            except Exception as e:
                logger.error("[DB Handler]", e)
                logger.error(f"[DB Handler] Insert item fail: name={name}, namespace={namespace}")
                return status.HTTP_500_INTERNAL_SERVER_ERROR

    def delete_item(self, name: str, namespace: str) -> Tuple[int, str]:
        with Session(engine) as session:
            try:
                # Query item and delete
                item = session.query(Pod).filter(Pod.name == name, Pod.namespace == namespace).first()
                if item:
                    session.delete(item)
                else:
                    logger.warning(f"[DB Handler] Invalid service: namespace: {namespace}, name: {name}")
                    return (status.HTTP_422_UNPROCESSABLE_ENTITY, "Delete Service Fail: Invalid Service")
                session.commit()
                logger.info(f"[DB Handler] Delete item success: name={name}, namespace={namespace}")
                return (status.HTTP_200_OK, "Delete Service Success")

            except Exception as e:
                logger.error("[DB Handler]", e)
                logger.error(f"[DB Handler] Delete item fail: name={name}, namespace={namespace}")
                return (status.HTTP_500_INTERNAL_SERVER_ERROR, "Delete Service Fail")


# Create DB handler
dh = DatabaseHandler()
