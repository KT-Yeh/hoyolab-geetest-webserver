import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.database import Database
from src.models import GeetestChallenge, User
from src.schemas import Game, GeetestResult

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s-%(levelname)s-%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("shutdown")
async def shutdown_event():
    """程式結束前會呼叫此函式"""
    await Database.close()


@app.get("/")
async def read_root():
    """根路徑，確認狀態用"""
    return {"status": "ok"}


async def check_user(discord_id: int) -> bool:
    """Check if the user exists"""
    user = await Database.select_one(User, User.discord_id.is_(discord_id))
    return False if user is None else True


@app.get("/geetest/{game}/{discord_id}/{gt}/{challenge}", response_class=HTMLResponse)
async def solve_geetest(
    request: Request,
    game: Game,
    discord_id: int,
    gt: str,
    challenge: str,
):
    """機器人產生連結請求本路徑，回傳解鎖圖形驗證的網頁"""
    if (await check_user(discord_id)) is False:
        raise HTTPException(404, detail="使用者不存在資料庫內，請先設定 Cookie 註冊使用者")
    if len(gt) < 30 or len(challenge) < 30:
        raise HTTPException(404, detail="參數錯誤，請回到小幫手重新產生連結")

    context = {
        "request": request,
        "game": game.value,
        "discord_id": discord_id,
        "gt": gt,
        "challenge": challenge,
    }
    logging.info(context)
    return templates.TemplateResponse("index.html", context)


@app.post("/geetest/{game}/{discord_id}", response_class=PlainTextResponse)
async def save_geetest_result(
    game: Game,
    discord_id: int,
    result: GeetestResult,
):
    """使用者通過圖形驗證後頁面請求本路徑，儲存結果資料"""
    logging.info(f"{type(discord_id)} {result.dict()}")
    if (await check_user(discord_id)) is False:
        raise HTTPException(404, detail="使用者不存在資料庫內，請先設定 Cookie 註冊使用者")

    await Database.insert_or_replace(
        GeetestChallenge(
            discord_id,
            genshin={
                "challenge": result.geetest_challenge,
                "validate": result.geetest_validate,
                "seccode": result.geetest_seccode,
            },
        )
    )
    return "驗證結果已保存至資料庫！可以回到小幫手使用 /daily 指令簽到"


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """所有 HTTP 錯誤導向此頁面"""
    context = {"request": request, "error": exc.detail}
    return templates.TemplateResponse("error.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
