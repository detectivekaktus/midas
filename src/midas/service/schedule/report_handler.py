from asyncio import sleep
from calendar import monthrange
from datetime import date
from time import perf_counter
from typing import override

from midas.loggers import app_logger

from midas.service.abstract_notifier import AbstractNotifier
from midas.service.schedule.abstract_handler import AbstractHandler
from midas.usecase.report import GenerateReportUsecase


class ReportHandler(AbstractHandler):
    @override
    def __init__(self, notifier: AbstractNotifier, update_interval: int = 600) -> None:
        super().__init__(notifier, update_interval)
        self._generate_repo = GenerateReportUsecase()

    @override
    async def loop(self) -> None:
        while True:
            app_logger.info("Started monthly report generation.")
            start = perf_counter()

            today = date.today()
            last_month_day = monthrange(today.year, today.month)[1]
            if today.day != last_month_day:
                app_logger.info(
                    f"Finished report generation too soon because {today} is not the end of the month."
                )
                await sleep(self._UPDATE_INTERVAL)
                continue

            reports_generated = 0
            # WIP: missing GetAllUsersUsecase

            app_logger.info(
                f"Finished generating {reports_generated} reports in {round(perf_counter() - start, 3)} seconds."
            )
            await sleep(self._UPDATE_INTERVAL)
