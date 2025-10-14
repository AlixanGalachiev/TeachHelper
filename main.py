import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.route_user import router as users_router
from app.routes.route_classroom import router as classrooms_router
from app.routes.route_auth import router as auth_router
# from app.routes.route_work import router as work_router


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
	app.include_router(users_router)
	app.include_router(classrooms_router)
	app.include_router(auth_router)
	# app.include_router(work_router)


	return app


app = create_app()

if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
