import logging
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from _pytest.reports import TestReport
from _pytest.terminal import TerminalReporter

from app.main import create_app
from app.sample_data import seed_sample_data


test_report_logger = logging.getLogger("test_report")


def pytest_runtest_logstart(nodeid: str, location: Any) -> None:
    test_report_logger.info("TEST CASE --> %s", nodeid)
    test_report_logger.info("INFO --> Test execution started")


def pytest_runtest_logreport(report: TestReport) -> None:
    if report.when != "call":
        return
    test_report_logger.info("INFO --> Test duration %.3fs", report.duration)
    test_report_logger.info("TEST STATUS --> %s", report.outcome.upper())


def pytest_terminal_summary(
    terminalreporter: TerminalReporter, exitstatus: int, config: Any
) -> None:
    passed = [report for report in terminalreporter.stats.get("passed", []) if report.when == "call"]
    failed = [report for report in terminalreporter.stats.get("failed", []) if report.when == "call"]
    skipped = [report for report in terminalreporter.stats.get("skipped", []) if report.when == "call"]
    total = len(passed) + len(failed) + len(skipped)
    status = "FAILED" if failed else "PASSED"

    terminalreporter.write_sep("=", "TEST REPORT")
    terminalreporter.write_line("TEST STATUS --> {}".format(status))
    terminalreporter.write_line(
        "TEST CASES --> {} | PASSED --> {} | FAILED --> {} | SKIPPED --> {}".format(
            total, len(passed), len(failed), len(skipped)
        )
    )
@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    database_path = tmp_path / "orders.sqlite3"
    application = create_app("sqlite:///{}".format(database_path.as_posix()))
    with TestClient(application) as test_client:
        with test_client.app.state.engine.begin() as connection:
            seed_sample_data(connection)
        yield test_client