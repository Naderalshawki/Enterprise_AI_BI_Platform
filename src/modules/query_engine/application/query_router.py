from __future__ import annotations

import logging
from typing import Dict

from src.modules.query_engine.domain.entities import (
    QueryContext,
    QueryRequest,
    QueryResult,
)
from src.modules.query_engine.domain.enums import (
    QueryIntent,
    QuerySource,
)
from src.modules.query_engine.domain.interfaces import (
    QuerySourceAdapter,
)


logger = logging.getLogger(__name__)


class QueryRouter:
    """
    المسؤول عن توجيه Query إلى مصدر البيانات المناسب.

    QueryRouter لا يقوم بـ:

        - تصنيف السؤال.
        - إنشاء QueryContext.
        - توليد SQL.
        - تنفيذ SQL.
        - تنفيذ RAG.
        - استدعاء LLM.

    هذه المسؤوليات موجودة في الطبقات المناسبة.

    دوره فقط:

        QueryContext.source
                ↓
        تحديد Adapter
                ↓
        Adapter.execute()
                ↓
        QueryResult

    في الإصدار الحالي:

        QuerySource.CHAT_DATABASE
                ↓
        ChatDatabaseAdapter
    """

    # ==========================================================
    # Initialization
    # ==========================================================

    def __init__(
        self,
        adapters: dict[str, QuerySourceAdapter] | None = None,
    ) -> None:
        """
        إنشاء QueryRouter.

        Parameters
        ----------
        adapters:
            Registry يحتوي على الـAdapters المدعومة.

        مثال:

            {
                "chat_database": ChatDatabaseAdapter(...)
            }
        """

        self._adapters: Dict[
            str,
            QuerySourceAdapter,
        ] = {}

        if adapters:
            for name, adapter in adapters.items():
                self.register_adapter(
                    name,
                    adapter,
                )

    # ==========================================================
    # Route
    # ==========================================================

    async def route(
        self,
        request: QueryRequest,
        context: QueryContext,
    ) -> QueryResult:
        """
        توجيه الاستعلام إلى الـAdapter المناسب.

        Flow:

            QueryRequest
                  +
            QueryContext
                  ↓
            Resolve Source
                  ↓
            Resolve Adapter
                  ↓
            Adapter.execute()
                  ↓
            QueryResult
        """

        if request is None:
            raise ValueError(
                "QueryRequest cannot be None."
            )

        if context is None:
            raise ValueError(
                "QueryContext cannot be None."
            )

        source_name = context.source.value

        adapter = self._resolve_adapter(
            source_name
        )

        logger.info(
            "[QueryRouter] "
            "Routing query | "
            "query_id=%s | "
            "source=%s",
            request.query_id,
            source_name,
        )

        result = await adapter.execute(
            request=request,
            context=context,
        )

        if result is None:
            raise RuntimeError(
                "QuerySourceAdapter returned None."
            )

        return result

    # ==========================================================
    # Resolve Adapter
    # ==========================================================

    def _resolve_adapter(
        self,
        source_name: str,
    ) -> QuerySourceAdapter:
        """
        الحصول على Adapter حسب اسم المصدر.
        """

        if not source_name:
            raise ValueError(
                "Query source cannot be empty."
            )

        adapter = self._adapters.get(
            source_name
        )

        if adapter is None:
            raise ValueError(
                f"No QuerySourceAdapter registered "
                f"for source: {source_name}"
            )

        return adapter

    # ==========================================================
    # Register Adapter
    # ==========================================================

    def register_adapter(
        self,
        source_name: str,
        adapter: QuerySourceAdapter,
    ) -> None:
        """
        تسجيل Adapter جديد.

        يسمح لاحقًا بإضافة مصادر جديدة
        بدون تعديل QueryRouter نفسه.
        """

        if not source_name:
            raise ValueError(
                "source_name cannot be empty."
            )

        if adapter is None:
            raise ValueError(
                "adapter cannot be None."
            )

        if not isinstance(
            adapter,
            QuerySourceAdapter,
        ):
            raise TypeError(
                "adapter must implement "
                "QuerySourceAdapter."
            )

        if source_name in self._adapters:
            raise ValueError(
                f"Adapter already registered "
                f"for source: {source_name}"
            )

        self._adapters[
            source_name
        ] = adapter

        logger.info(
            "[QueryRouter] "
            "Adapter registered | source=%s",
            source_name,
        )

    # ==========================================================
    # Unregister Adapter
    # ==========================================================

    def unregister_adapter(
        self,
        source_name: str,
    ) -> bool:
        """
        إزالة Adapter.

        Returns:
            True إذا تم الحذف.
            False إذا لم يكن موجودًا.
        """

        if not source_name:
            return False

        adapter = self._adapters.pop(
            source_name,
            None,
        )

        if adapter is None:
            return False

        logger.info(
            "[QueryRouter] "
            "Adapter unregistered | source=%s",
            source_name,
        )

        return True

    # ==========================================================
    # Get Adapter
    # ==========================================================

    def get_adapter(
        self,
        source_name: str,
    ) -> QuerySourceAdapter | None:
        """
        الحصول على Adapter بدون رفع Exception.
        """

        return self._adapters.get(
            source_name
        )

    # ==========================================================
    # Has Adapter
    # ==========================================================

    def has_adapter(
        self,
        source_name: str,
    ) -> bool:
        """
        التحقق من وجود Adapter.
        """

        return source_name in self._adapters

    # ==========================================================
    # Supported Sources
    # ==========================================================

    @property
    def supported_sources(self) -> tuple[str, ...]:
        """
        إرجاع مصادر البيانات المدعومة حاليًا.
        """

        return tuple(
            self._adapters.keys()
        )

    # ==========================================================
    # Intent Support
    # ==========================================================

    @staticmethod
    def is_supported_intent(
        intent: QueryIntent,
    ) -> bool:
        """
        التحقق من أن Intent يمكن توجيهه عبر
        Query Engine الحالي.

        حاليًا Query Engine مخصصة لمسار Database،
        لذلك DATA وSCHEMA وDATABASE_INFO مدعومة.

        UNKNOWN غير مدعومة.
        """

        return intent in {
            QueryIntent.DATA,
            QueryIntent.SCHEMA,
            QueryIntent.DATABASE_INFO,
        }

    # ==========================================================
    # Health Check
    # ==========================================================

    async def health_check(
        self,
    ) -> dict[str, bool]:
        """
        فحص صحة جميع الـAdapters المسجلة.
        """

        results: dict[str, bool] = {}

        for source_name, adapter in (
            self._adapters.items()
        ):
            try:

                results[source_name] = (
                    await adapter.health_check()
                )

            except Exception:

                logger.exception(
                    "[QueryRouter] "
                    "Adapter health check failed | "
                    "source=%s",
                    source_name,
                )

                results[source_name] = False

        return results