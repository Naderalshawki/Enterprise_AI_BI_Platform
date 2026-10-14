from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # تم إضافة الاستدعاء هنا

from src.bootstrap import (
    close_database,
    create_query_engine,
)

from src.modules.llm.interfaces.router import (
    router as llm_router,
)

from src.modules.chat_database.interfaces.router import (
    router as chat_database_router,
)

from src.modules.multi_agent.interfaces.router import (
    router as bi_agent_router,
)

from src.modules.query_engine.interfaces.api_router import (
    create_query_engine_router,
)

from src.services.schools_service import (
    fetch_schools_data,
)


# ==========================================================
# Query Engine Router
# ==========================================================

query_engine_router = create_query_engine_router(
    create_query_engine()
)


# ==========================================================
# Application Lifespan
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة تطبيق FastAPI.

    Startup:
        تشغيل التطبيق وتجهيز البيئة.

    Shutdown:
        إغلاق موارد قاعدة البيانات بشكل آمن.
    """

    # ------------------------------------------------------
    # Startup
    # ------------------------------------------------------

    yield

    # ------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------

    await close_database()


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="AI Business Intelligence Platform",
    description=(
        "Enterprise-grade AI Orchestrator "
        "and Multi-Tenant BI Engine"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ==========================================================
# CORS Middleware (للسماح باتصال الواجهة بالسيرفر)
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يسمح لأي واجهة بالاتصال (مهم جداً لـ Streamlit)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Routers
# ==========================================================

# ----------------------------------------------------------
# LLM
# ----------------------------------------------------------

app.include_router(
    llm_router
)


# ----------------------------------------------------------
# Chat Database
# ----------------------------------------------------------

app.include_router(
    chat_database_router
)


# ----------------------------------------------------------
# Query Engine
# ----------------------------------------------------------

app.include_router(
    query_engine_router
)


# ----------------------------------------------------------
# Multi-Agent BI
# ----------------------------------------------------------

app.include_router(
    bi_agent_router
)


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get(
    "/",
    tags=["System"],
)
async def root():
    """
    نقطة الدخول الرئيسية للنظام.

    تستخدم للتحقق من أن التطبيق يعمل
    وأن الوحدات الأساسية محملة.
    """

    return {
        "message": (
            "AI BI Platform is running smoothly."
        ),
        "status": "ok",
        "modules_loaded": [
            "LLM",
            "ChatDatabase",
            "QueryEngine",
            "Multi-Agent",
        ],
    }


# ==========================================================
# External APIs
# ==========================================================

@app.get(
    "/api/external/schools",
    tags=["External APIs"],
)
async def get_schools_endpoint():
    """
    جلب بيانات المدارس من واجهة
    الـExternal API الخارجية.
    """

    data = fetch_schools_data()

    return {
        "status": "success",
        "data": data,
    }