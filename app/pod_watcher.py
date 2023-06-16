import uuid
import threading
from kubernetes import watch

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
        w = watch.Watch()
        logger.info("[Pod Watcher] Watching pod start")

        # Stream's default timeout_seconds = minRequestTimeout(default=1800) ~ 2*minRequestTimeout
        for event in w.stream(v1.list_pod_for_all_namespaces, label_selector="app=test"):
            if self.stop_flag:
                w.stop()

            # Catch ADDED event
            elif event["type"] == "ADDED":
                metadata = event["object"].metadata
                logger.info(f"[Pod Watcher] Catch added pod: name={metadata.name}, namespace={metadata.namespace}")

                # Insert DB
                name = f"service-{uuid.uuid4()}"
                portname = event["object"].spec.containers[0].ports[0].name
                dh.insert_item(name=name, namespace=metadata.namespace, targetport=portname, labels={"app": "test"})

        logger.info("[Pod Watcher] Stop kubernetes handler")

    def stop(self) -> None:
        self.stop_flag = True
