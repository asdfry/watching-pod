import threading
from kubernetes import utils
from sqlalchemy import event

from app.ready import Pod, k8s_client, v1
from app.log_handler import logger


def on_insert(mapper, connection, target):
    """
    Create service when catching insert event
    """
    logger.info(f"[DB Watcher] Catch insert event: name={target.name}, namespace={target.namespace}")
    try:
        service_dict = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": target.name, "lables": {"app": "test"}, "namespace": target.namespace},
            "spec": {
                "selector": {"app": "test"},
                "ports": [{"port": 9000, "targetPort": target.targetport}],
                "type": "NodePort",
            },
        }
        utils.create_from_dict(k8s_client, service_dict)
        logger.info(f"[DB Watcher] Add service success: name={target.name}, namespace={target.namespace}")

    except Exception as e:
        logger.error("[DB Watcher]", e)
        logger.error(f"[DB Watcher] Add service fail: name={target.name}, namespace={target.namespace}")


def on_delete(mapper, connection, target):
    """
    Delete service when catching delete event
    """
    logger.info(f"[DB Watcher] Catch delete event: name={target.name}, namespace={target.namespace}")
    try:
        v1.delete_namespaced_service(name=target.name, namespace=target.namespace)
        logger.info(f"[DB Watcher] Delete service success: name={target.name}, namespace={target.namespace}")

    except Exception as e:
        logger.error("[DB Watcher]", e)
        logger.error(f"[DB Watcher] Delete service fail: name={target.name}, namespace={target.namespace}")


class DatabaseWatcher(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.stop_flag = False
        logger.info("[DB Watcher] Init database watcher")

        # Register event listener
        event.listen(Pod, "after_insert", on_insert)
        event.listen(Pod, "after_delete", on_delete)
        logger.info("[DB Watcher] Register event listener")
