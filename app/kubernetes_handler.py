import uuid
import threading
from fastapi import status
from kubernetes import client, config, watch, utils
from app.database_handler import dh
from app.log_handler import logger


class KubernetesHandler(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        config.load_kube_config()
        self.k8s_client = client.ApiClient()
        self.v1 = client.CoreV1Api()
        self.stop_flag = False

    def run(self):
        # Watching pod start with label selector (app:test)
        w = watch.Watch()
        target_labels = {"app": "test"}
        logger.info("[K8S] Watching pod start")

        # Stream's default timeout_seconds = minRequestTimeout(default=1800) ~ 2*minRequestTimeout
        for event in w.stream(self.v1.list_pod_for_all_namespaces, label_selector="app=test"):
            # Gracefully shutdown
            if self.stop_flag:
                w.stop()

            # Catch ADDED event
            elif event["type"] == "ADDED":
                metadata = event["object"].metadata
                logger.info(f"[K8S] Catch added pod: name={metadata.name}, namespace={metadata.namespace}")

                # Create service using dict
                name = f"service-{uuid.uuid4()}"
                portname = event["object"].spec.containers[0].ports[0].name
                service_dict = {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": name, "lables": target_labels, "namespace": metadata.namespace},
                    "spec": {
                        "selector": target_labels,
                        "ports": [{"port": 9000, "targetPort": portname}],
                        "type": "NodePort",
                    },
                }
                utils.create_from_dict(self.k8s_client, service_dict)
                logger.info(f"[K8S] Add service success: name={name}, namespace={metadata.namespace}, targetport={portname}")

                # Insert DB
                result = dh.insert_item(name=name, namespace=metadata.namespace, targetport=portname, labels=target_labels)
                if not result == 200:
                    logger.warning(f"[K8S] Delete service created just before because insert item failed")
                    self.delete_service(name, metadata.namespace)

        logger.info("[K8S] Stop kubernetes handler")

    def stop(self) -> None:
        self.stop_flag = True

    def delete_service(self, name: str, namespace: str) -> int:
        try:
            self.v1.delete_namespaced_service(name=name, namespace=namespace)
            logger.info(f"[K8S] Delete service success: name={name}, namespace={namespace}")
            return status.HTTP_200_OK
        except:
            logger.error(f"[K8S] Delete service fail: name={name}, namespace={namespace}")
            return status.HTTP_500_INTERNAL_SERVER_ERROR
