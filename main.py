import json
import uuid
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.route_auth import router as auth_router
from app.routes.route_classroom import router as classroom_router
from app.routes.route_students import router as teacher_students_router
from app.routes.route_students import router2 as student_teachers_router
from app.routes.route_tasks import router as tasks_router
from app.routes.route_subjects import router as subjects_router
from app.routes.route_works import router as works_router
from app.schemas.schema_work import WorkAllFilters


def create_app() -> FastAPI:
    app = FastAPI(title="RU-Lang MVP API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/filesWork", StaticFiles(directory="public/filesWork"), name="filesWork")

    # Роутеры
    app.include_router(auth_router)
    app.include_router(classroom_router)
    app.include_router(teacher_students_router)
    app.include_router(student_teachers_router)
    app.include_router(tasks_router)
    app.include_router(subjects_router)
    app.include_router(works_router)


    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
