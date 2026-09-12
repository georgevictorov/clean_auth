from datetime import UTC, datetime


class SystemClock:
    @staticmethod
    def now() -> datetime:
        return datetime.now(UTC)
