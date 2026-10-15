# Import every model so Base.metadata (used by Alembic and tests) knows all tables.
from app.models.athlete import Athlete  # noqa: F401
from app.models.sync_record import SyncRecord  # noqa: F401
from app.models.test_result import TestResult  # noqa: F401
from app.models.test_submission import TestSubmission  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.benchmark_norm import BenchmarkNorm  # noqa: F401
from app.models.shortlist import Shortlist  # noqa: F401
