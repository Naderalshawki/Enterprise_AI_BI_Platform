from enum import Enum


class QueryStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryIntent(str, Enum):
    DATA = "data"
    SCHEMA = "schema"
    DATABASE_INFO = "database_info"
    UNKNOWN = "unknown"


class QueryExecutionMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"


class QuerySource(str, Enum):
    CHAT_DATABASE = "chat_database"
    UNKNOWN = "unknown"


class QueryPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"