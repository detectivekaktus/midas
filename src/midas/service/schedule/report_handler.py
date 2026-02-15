from asyncio import sleep
from calendar import monthrange
from datetime import date
from time import perf_counter
from typing import Any, override

from midas.loggers import app_logger

from midas.service.abstract_notifier import AbstractNotifier
from midas.service.schedule.abstract_handler import AbstractHandler
from midas.usecase.report import GenerateReportUsecase
from midas.usecase.user import GetAllUsersUsecase
from midas.util.enums import Currency, TransactionType


class ReportHandler(AbstractHandler):
    @override
    def __init__(
        self, notifier: AbstractNotifier, update_interval: int = 3600 * 24
    ) -> None:
        super().__init__(notifier, update_interval)
        self._generate_report = GenerateReportUsecase()
        self._get_users = GetAllUsersUsecase()

    def _generate_notifier_message(
        self, report: dict[str, Any], currency: Currency
    ) -> str:
        msg = "MONTHLY REPORT:\n"
        msg += "\n".join(
            [
                f"- {name.title().replace("_", " ")}: {currency.name} {value}"
                for name, value in report["accounts"].items()
                if name != TransactionType.INCOME.name.lower()
            ]
        )
        msg += f"\nOverall monthly balance: {currency.name} {report["result"]}"
        return msg

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
            users = await self._get_users.execute()
            for user in users:
                report = await self._generate_report.execute(user.id)

                if user.send_notifications:
                    msg = self._generate_notifier_message(
                        report, Currency(user.currency_id)
                    )
                    await self._notifier.notify(user.id, msg)

                reports_generated += 1

            app_logger.info(
                f"Finished generating {reports_generated} reports in {round(perf_counter() - start, 3)} seconds."
            )
            await sleep(self._UPDATE_INTERVAL)
