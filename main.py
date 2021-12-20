from fastapi.responses import ORJSONResponse
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from concurrent.futures.process import ProcessPoolExecutor

from routes.home import router as home
from routes.login import router as login
from routes.api import router as api

app = FastAPI(title='tradestation focusxgen app', openapi_url="/openapi.json", default_response_class=ORJSONResponse)

app.mount("/static", StaticFiles(directory="assets/static"), name="static")

app.include_router(home)
app.include_router(login)
app.include_router(api)

@app.on_event("shutdown")
async def on_shutdown():
    print('Check Shutdown')


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3000, log_level='debug')