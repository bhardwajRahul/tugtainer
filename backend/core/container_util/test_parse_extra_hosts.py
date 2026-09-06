from backend.core.container_util.parse_extra_hosts import parse_extra_hosts


def test_parse_extra_hosts():
    assert parse_extra_hosts(None) is None
    assert parse_extra_hosts([]) is None

    hosts = [
        "host.docker.internal:host-gateway",
        "test.local:127.0.0.1",
        "invalid_host",  # missing colon, should be ignored
        "ipv6:[::1]",  # valid colon separation
    ]

    expected = [
        ("host.docker.internal", "host-gateway"),
        ("test.local", "127.0.0.1"),
        ("ipv6", "[::1]"),
    ]

    assert parse_extra_hosts(hosts) == expected
