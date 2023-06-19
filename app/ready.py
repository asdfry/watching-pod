import time
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import JSON
from kubernetes import client, config

from app.log_handler import logger


# Wait for db container up
logger.info("[Ready] Waiting for db container up . . .")
time.sleep(15)

# Create an engine to connect to the MySQL database (Connection closed every hour)
engine = create_engine("mysql+pymysql://intstr:0604@localhost:3306/ten?charset=utf8mb4", pool_recycle=3600)
logger.info("[Ready] Create sqlalchemy engine")

# Create a base class for declarative models
Base = declarative_base()
logger.info("[Ready] Create sqlalchemy base class")


# Define table model
class Pod(Base):
    __tablename__ = "pod"
    name = Column(String(255), primary_key=True)
    namespace = Column(String(255), nullable=False)
    targetport = Column(String(255), nullable=False)
    labels = Column(JSON, nullable=False)


# Create the table in the database
Base.metadata.create_all(engine)
logger.info("[Ready] Create pod table")

# Load kubernetes config
config.load_kube_config()
logger.info("[Ready] Load kubernetes config")

# Create kubernetes client
k8s_client = client.ApiClient()
logger.info("[Ready] Create kubernetes client")

# Create kubernetes v1
v1 = client.CoreV1Api()
logger.info("[Ready] Create kubernetes v1")
