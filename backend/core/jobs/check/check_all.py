import asyncio
import logging
from typing import Final

from sqlalchemy import select

from backend.core.jobs.jobs_coordinator import host_job_coordinator
from backend.core.jobs.jobs_results import job_to_notification_result
from backend.core.jobs.jobs_schemas import Job
from backend.core.notifications_core import send_job_notification
from backend.db.session import async_session_maker
from backend.modules.hosts.hosts_model import HostsModel


async def check_all_hosts(
    manual: bool = False,
) -> None:
    """
    Check all containers of all hosts
    :param manual: manual check includes all containers
    """
    logger: Final = logging.getLogger("check_all_hosts")

    try:
        logger.info("Start checking of all containers for all hosts")

        async with async_session_maker() as session:
            hosts: Final = (
                (await session.execute(select(HostsModel).where(HostsModel.enabled)))
                .scalars()
                .all()
            )

        finished: dict[int, Job] = {}

        async def check_host(host: HostsModel) -> None:
            try:
                runtime = await host_job_coordinator.submit(
                    host,
                    "check",
                    names=None,
                    manual=manual,
                    wait=True,
                )
                if runtime.job:
                    finished[host.id] = runtime.job
            except Exception:
                logger.exception(f"Failed to check host {host.name}")

        _ = await asyncio.gather(*(check_host(host) for host in hosts))
        try:
            await send_job_notification(
                [job_to_notification_result(job) for job in finished.values()]
            )
        except Exception:
            logger.exception("Failed to send notification")

    except Exception:
        logger.exception("Error while checking all containers for all hosts")
