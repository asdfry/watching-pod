import time
import uuid
import threading

from app.ready import v1
from app.database_handler import dh
from app.log_handler import logger


class PodWatcher(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.stop_flag = False
        logger.info("[Pod Watcher] Init pod watcher")

    def run(self):
        """
        Insert db when catching added pod event (target label = {app:test})
        """
        logger.info("[Pod Watcher] Watching pod start")
        uids = []

        # Stream's default timeout_seconds = minRequestTimeout(default=1800) ~ 2*minRequestTimeout
        while True:
            if self.stop_flag:
                break

            ret = v1.list_namespaced_pod(namespace="default")
            for item in ret.items:
                uid = item.metadata.uid
                if uid in uids:
                    continue
                else:  # Catch ADDED event
                    logger.info(f"[Pod Watcher] Catch added pod: name={item.metadata.name}, namespace={item.metadata.namespace}")

                    # Insert DB
                    name = f"service-{uuid.uuid4()}"
                    portname = item.spec.containers[0].ports[0].name
                    dh.insert_item(name=name, namespace=item.metadata.namespace, targetport=portname, labels={"app": "test"})
                    uids.append(uid)
                    
            time.sleep(2)

        logger.info("[Pod Watcher] Stop kubernetes handler")

    def stop(self) -> None:
        self.stop_flag = True
