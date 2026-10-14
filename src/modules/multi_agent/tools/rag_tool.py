from __future__ import annotations

import logging
from typing import Any

from src.modules.multi_agent.domain.bi_context import BIContext


logger = logging.getLogger(__name__)


class RAGTool:
    """
    RAG Tool
    ========

    طبقة الربط بين Multi-Agent وبين خدمة RAG الخارجية.

    حاليًا:
        - RAG Service غير متوفر بعد.
        - لا توجد بيانات Mock.
        - الأداة جاهزة لاستقبال RAG Service الحقيقي.

    لاحقًا:

        RAGTool
           ↓
        RAGService
           ↓
        Document Retrieval
           ↓
        Vector Database
           ↓
        Reranking / Hybrid Search
           ↓
        Retrieved Context
    """

    def __init__(
        self,
        rag_service: Any | None = None,
    ):
        """
        إنشاء RAGTool.

        rag_service:
            خدمة RAG الحقيقية عندما يسلّمها زميل المشروع.

            حاليًا يمكن أن تكون None.
        """

        self.name = "RAGTool"

        self.description = (
            "يستخدم للبحث في المستندات والملفات النصية "
            "واستخراج المعلومات ذات الصلة بالسؤال."
        )

        self._rag_service = rag_service

    # ==========================================================
    # Public API
    # ==========================================================

    async def execute(
        self,
        inputs: dict[str, Any],
        context: BIContext,
    ) -> Any:
        """
        تنفيذ مهمة البحث في المستندات.

        لا يوجد Mock Result.

        إذا لم يتم ربط RAG Service بعد:
            يتم تسجيل خطأ واضح وإيقاف المهمة.

        بعد وصول RAG Service:
            يتم تمرير الطلب إليه وإرجاع النتيجة.
        """

        query = self._extract_query(
            inputs=inputs,
            context=context,
        )

        logger.info(
            "[Tool: %s] Executing RAG query: %s",
            self.name,
            query,
        )

        # ------------------------------------------------------
        # Validate RAG Service
        # ------------------------------------------------------

        if self._rag_service is None:

            error_message = (
                "RAG service is not configured yet. "
                "Waiting for the RAG implementation."
            )

            logger.warning(
                "[Tool: %s] %s",
                self.name,
                error_message,
            )

            context.add_error(
                self.name,
                error_message,
            )

            raise RuntimeError(
                error_message
            )

        try:

            # --------------------------------------------------
            # Execute RAG Service
            # --------------------------------------------------

            result = await self._call_rag_service(
                query=query,
                context=context,
            )

            # --------------------------------------------------
            # Validate Result
            # --------------------------------------------------

            if result is None:
                raise RuntimeError(
                    "RAG service returned no result."
                )

            # --------------------------------------------------
            # Store Result
            # --------------------------------------------------

            self._store_result(
                result=result,
                context=context,
            )

            logger.info(
                "[Tool: %s] RAG retrieval completed successfully.",
                self.name,
            )

            return result

        except Exception as exc:

            logger.exception(
                "[Tool: %s] RAG execution failed.",
                self.name,
            )

            context.add_error(
                self.name,
                str(exc),
            )

            raise

    # ==========================================================
    # Query Extraction
    # ==========================================================

    @staticmethod
    def _extract_query(
        inputs: dict[str, Any],
        context: BIContext,
    ) -> str:
        """
        استخراج سؤال البحث.

        الأولوية:
            inputs["query"]
            ثم context.question
        """

        query = inputs.get(
            "query"
        )

        if query is None:
            query = context.question

        query = str(
            query
        ).strip()

        if not query:
            raise ValueError(
                "RAG query cannot be empty."
            )

        return query

    # ==========================================================
    # RAG Service Adapter
    # ==========================================================

    async def _call_rag_service(
        self,
        query: str,
        context: BIContext,
    ) -> Any:
        """
        Adapter لاستدعاء RAG Service.

        مهم:
        هذه الدالة تحتوي فقط على Contract مرن مؤقتًا،
        لأن واجهة RAG Service الحقيقية لم تصل بعد.

        عند وصول كود زميلك سنطابقها مع الـAPI الحقيقي
        بدل اختراع واجهة من عندنا.
        """

        service = self._rag_service

        search = getattr(
            service,
            "search",
            None,
        )

        if not callable(search):
            raise TypeError(
                "Configured RAG service must provide "
                "an async search() method."
            )

        # --------------------------------------------------
        # Try passing execution context when supported.
        # --------------------------------------------------

        try:

            return await search(
                query=query,
                user_id=context.user_id,
                session_id=context.session_id,
            )

        except TypeError:

            # ------------------------------------------------
            # Temporary compatibility fallback.
            #
            # Some RAG implementations may expose only:
            #
            #     search(query)
            #
            # Until we inspect the real service.
            # ------------------------------------------------

            return await search(
                query
            )

    # ==========================================================
    # Store Result
    # ==========================================================

    @staticmethod
    def _store_result(
        result: Any,
        context: BIContext,
    ) -> None:
        """
        تخزين نتيجة RAG في BIContext.

        ندعم مؤقتًا:
            - string
            - list
            - dict
            - أي structured result
        """

        # ------------------------------------------------------
        # Store raw RAG context
        # ------------------------------------------------------

        context.rag_context = result

        # ------------------------------------------------------
        # Structured result
        # ------------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            context.set_rag_result(
                result=result,
                context=result.get(
                    "context",
                    result,
                ),
            )

        elif isinstance(
            result,
            list,
        ):

            context.set_rag_result(
                result={
                    "documents": result,
                    "count": len(result),
                },
                context=result,
            )

        else:

            context.set_rag_result(
                result={
                    "content": str(result),
                },
                context=result,
            )

        # ------------------------------------------------------
        # Backward-compatible metadata
        # ------------------------------------------------------

        context.metadata[
            "rag_context"
        ] = result

    # ==========================================================
    # Service Access
    # ==========================================================

    def set_rag_service(
        self,
        rag_service: Any,
    ) -> None:
        """
        ربط RAG Service بعد توفره.

        مفيدة أثناء Bootstrap / Dependency Injection.
        """

        if rag_service is None:
            raise ValueError(
                "rag_service cannot be None."
            )

        self._rag_service = rag_service

        logger.info(
            "[Tool: %s] RAG service configured successfully.",
            self.name,
        )

    def is_configured(self) -> bool:
        """
        هل تم ربط RAG Service؟
        """

        return self._rag_service is not None