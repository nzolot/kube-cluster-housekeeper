import kubernetes
import logging
import os
import sys

log = logging.getLogger()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
log.setLevel(logging.getLevelName(os.getenv('LOG_LEVEL', "INFO")))

def _load_kube_config(v = None):
    if v is not None:
        kubernetes.config.load_kube_config(v)
    else:
        if 'KUBECONFIG' in os.environ:
            log.info("Configuring kube auth with KUBECONFIG")
            kubernetes.config.load_kube_config(os.environ.get('KUBECONFIG'))
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            log.info("Configuring kube auth with KUBERNETES_SERVICE_HOST")
            kubernetes.config.load_incluster_config()


def _watch_kube_nodes(timeout = 0):
    log.info("Waiting for events from nodes")
    _w = kubernetes.watch.Watch()
    for _event in _w.stream(kubernetes.client.CoreV1Api().list_node,
                            timeout_seconds=timeout):
        node_name = _event["object"].metadata.name
        event_type = _event["type"]

        delete_candidate   = False
        delete_tobedelete  = False
        delete_unreachable = False

        log.info("Node '%s': Event '%s': Received" % (event_type,node_name))
        if _event["object"].spec.taints is not None:
            for taint in _event["object"].spec.taints:
                if taint.key == "DeletionCandidateOfClusterAutoscaler":
                    log.info("Node '%s': Event '%s': %s" % (event_type,node_name,taint.key))
                    delete_candidate = True
                if taint.key == "ToBeDeletedByClusterAutoscaler":
                    log.info("Node '%s': Event '%s': %s" % (event_type,node_name,taint.key))
                    delete_tobedelete = True
                if taint.key == "node.kubernetes.io/unreachable":
                    log.info("Node '%s': Event '%s': %s" % (event_type,node_name,taint.key))
                    delete_unreachable = True

        if delete_candidate and delete_tobedelete and delete_unreachable:
            log.info("Node '%s': Event '%s': Deleting node from cluster due to taints" % (event_type,node_name))
            try:
                kubernetes.client.CoreV1Api().delete_node(name=node_name)
            except kubernetes.client.exceptions.ApiException as e:
                if e.status == 404:
                    log.info("Node '%s': Event '%s': Node does not exists" % (event_type,node_name))
                else:
                    log.error("Node '%s': Event '%s': Something went wrong" % (event_type,node_name))
                    log.error("{}".format(e))
                    sys.exit(1)

        log.info("Node '%s': Event '%s': Completed" % (_event["type"],node_name))

_load_kube_config()
_watch_kube_nodes()
