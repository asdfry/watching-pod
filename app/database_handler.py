import time
from typing import Dict, Tuple
from fastapi import status
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.types import JSON
from app.log_handler import logger


# Create an engine to connect to the MySQL database (Connection closed every hour)
engine = create_engine("mysql+pymysql://intstr:0604@localhost:3306/ten?charset=utf8mb4", pool_recycle=3600)
logger.info("[DB] Create engine")

# Create a base class for declarative models
Base = declarative_base()
logger.info("[DB] Create base class")


# Define table model
class Pod(Base):
    __tablename__ = "pod"
    name = Column(String(255), primary_key=True)
    namespace = Column(String(255), nullable=False)
    labels = Column(JSON, nullable=False)


class DatabaseHandler:
    def __init__(self) -> None:
        # Wait for db container up
        logger.info("[DB] Waiting for db container up . . .")
        time.sleep(15)

        # Create the table in the database
        Base.metadata.create_all(engine)
        logger.info("[DB] Create table")

    def health_check(self) -> bool:
        with Session(engine) as session:
            try:
                session.connection()
                return True
            except:
                return False

    def get_items(self) -> Tuple[int, list]:
        with Session(engine) as session:
            try:
                # Query all items from the Pod table
                items = session.query(Pod).all()
                pods = [
                    {"name": item.name, "namespace": item.namespace, "labels": item.labels} for item in items
                ]
                logger.info("[DB] Get items success")
                return (status.HTTP_200_OK, pods)
            except:
                logger.error("[DB] Get items fail")
                return (status.HTTP_500_INTERNAL_SERVER_ERROR, [])

    def insert_item(self, name: str, namespace: str, labels: Dict) -> int:
        with Session(engine) as session:
            try:
                # Create item and insert
                item = Pod(name=name, namespace=namespace, labels=labels)
                session.add(item)
                session.commit()
                logger.info("[DB] Insert item success")
                return status.HTTP_200_OK
            except:
                logger.error("[DB] Insert item fail")
                return status.HTTP_500_INTERNAL_SERVER_ERROR

    def delete_item(self, name: str, namespace: str) -> int:
        with Session(engine) as session:
            try:
                # Query item and delete
                item = session.query(Pod).filter(Pod.name == name, Pod.namespace == namespace).first()
                if item:
                    session.delete(item)
                session.commit()
                logger.info("[DB] Delete item success")
                return status.HTTP_200_OK
            except:
                logger.error("[DB] Delete item fail")
                return status.HTTP_500_INTERNAL_SERVER_ERROR


# Create DB handler
dh = DatabaseHandler()
