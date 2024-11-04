import requests
from kubernetes import client, config


def get_pod_placement():
    # Load kube config; for in-cluster, use load_incluster_config()
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pod_placement = []

    pods = v1.list_pod_for_all_namespaces(watch=False)
    for pod in pods.items:
        pod_info = {
            "pod_name": pod.metadata.name,
            "node_name": pod.spec.node_name
        }
        pod_placement.append(pod_info)

    return pod_placement


def query_prometheus(query):
    response = requests.get(
        f"{PROMETHEUS}/api/v1/query",
        params={"query": query}
    )
    return response.json().get("data", {}).get("result", [])


def get_node_stats():
    cpu_usage_query = 'avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) by (instance)'
    memory_usage_query = 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes'

    cpu_usage = query_prometheus(cpu_usage_query)
    memory_usage = query_prometheus(memory_usage_query)

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage
    }


def get_pod_stats():
    cpu_usage_query = 'sum(rate(container_cpu_usage_seconds_total[5m])) by (pod)'
    memory_usage_query = 'sum(container_memory_usage_bytes) by (pod)'

    cpu_usage = query_prometheus(cpu_usage_query)
    memory_usage = query_prometheus(memory_usage_query)

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage
    }


# Constants
PROMETHEUS = "http://<your-prometheus-server>:9090"


# Example usage for pod placement
if __name__ == "__main__":
    pod_placement = get_pod_placement()
    for pod in pod_placement:
        print(pod)

    # Example usage for node stats
    node_stats = get_node_stats()
    print(node_stats)

    # Example usage for pod stats
    pod_stats = get_pod_stats()
    print(pod_stats)
