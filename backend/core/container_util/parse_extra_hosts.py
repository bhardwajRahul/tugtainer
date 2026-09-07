def parse_extra_hosts(hosts: list[str] | None) -> list[tuple[str, str]] | None:
    if not hosts:
        return None
    res = []
    for h in hosts:
        parts = h.split(":", 1)
        if len(parts) == 2:
            res.append((parts[0], parts[1]))
    return res
