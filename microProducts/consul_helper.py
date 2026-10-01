"""
Consul helper: service registration and discovery via the Consul HTTP API.
"""
import os
import logging
import requests

logger = logging.getLogger(__name__)

CONSUL_HOST = os.environ.get('CONSUL_HOST', 'localhost')
CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
CONSUL_BASE = f'http://{CONSUL_HOST}:{CONSUL_PORT}'


def register_service(service_name: str, service_id: str, address: str, port: int) -> bool:
    """
    Register this service with the Consul agent.

    Args:
        service_name: logical name used for discovery (e.g. 'micro-products')
        service_id:   unique instance ID  (e.g. 'micro-products-1')
        address:      hostname/IP reachable by Consul (Docker service name)
        port:         listening port of this service
    Returns:
        True on success, False otherwise.
    """
    health_url = f'http://{address}:{port}/health'
    payload = {
        'ID':      service_id,
        'Name':    service_name,
        'Address': address,
        'Port':    port,
        'Tags':    ['flask', 'python'],
        'Check': {
            'HTTP':                            health_url,
            'Interval':                        '10s',
            'Timeout':                         '5s',
            'DeregisterCriticalServiceAfter':  '30s',
        },
    }
    try:
        resp = requests.put(
            f'{CONSUL_BASE}/v1/agent/service/register',
            json=payload,
            timeout=5,
        )
        if resp.status_code == 200:
            logger.info(f'[Consul] Registered "{service_id}" → {health_url}')
            return True
        logger.warning(f'[Consul] Registration failed ({resp.status_code}): {resp.text}')
        return False
    except requests.exceptions.RequestException as exc:
        logger.error(f'[Consul] Could not reach Consul agent: {exc}')
        return False


def discover_service(service_name: str) -> str:
    """
    Query Consul for a healthy instance of *service_name*.

    Returns:
        Base URL of the service (e.g. 'http://micro-products:5003').
    Raises:
        RuntimeError if no healthy instance is found.
    """
    try:
        resp = requests.get(
            f'{CONSUL_BASE}/v1/health/service/{service_name}',
            params={'passing': 'true'},
            timeout=5,
        )
        resp.raise_for_status()
        instances = resp.json()
        if not instances:
            raise RuntimeError(f'[Consul] No healthy instances found for "{service_name}"')
        svc = instances[0]['Service']
        address = svc['Address']
        port    = svc['Port']
        url = f'http://{address}:{port}'
        logger.info(f'[Consul] Discovered "{service_name}" → {url}')
        return url
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f'[Consul] Discovery request failed: {exc}') from exc
