from backend.modules.hosts.hosts_model import HostsModel


def get_host_cache_key(host: HostsModel) -> str:
    return f"{host.id}:{host.name}"
