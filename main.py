import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes.home import router as home
from routes.login import router as login

app = FastAPI(title='tradestation focusxgen app', openapi_url="/openapi.json")

app.mount("/static", StaticFiles(directory="assets/static"), name="static")

app.include_router(home)
app.include_router(login)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8020, log_level='debug')