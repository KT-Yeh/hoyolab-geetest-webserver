import logging
import os
from typing import Annotated, Literal

import genshin
from fastapi import FastAPI, HTTPException, Query, Request
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


@app.get("/geetest/{game}/{discord_id}", response_class=HTMLResponse)
async def solve_geetest(
    request: Request,
    game: Literal["genshin", "starrail_battlechronicle"],
    discord_id: int,
    gt: Annotated[str | None, Query(min_length=30)] = None,
    challenge: Annotated[str | None, Query(min_length=30)] = None,
):
    """機器人產生連結請求本路徑，回傳解鎖圖形驗證的網頁"""
    user = await Database.select_one(User, User.discord_id.is_(discord_id))
    if user is None:
        raise HTTPException(404, detail="使用者不存在資料庫內，請先設定 Cookie 註冊使用者")
    match game:
        case "genshin":  # 原神簽到
            pass
        case "starrail_battlechronicle":  # 星穹鐵道戰績 API
            cookie = user.cookie_starrail or user.cookie_default
            client = genshin.Client(
                cookie,
                lang="zh-tw",
                game=genshin.Game.STARRAIL,
                region=genshin.Region.OVERSEAS,
                proxy=os.getenv("PROXY_SERVER"),
            )
            try:
                await client.get_starrail_notes()
                raise HTTPException(404, detail="不需要圖形驗證！可以回到小幫手使用指令")
            except genshin.errors.GeetestError:
                mmt = await client.create_mmt()
                gt = mmt.gt
                challenge = mmt.challenge
            except Exception as e:
                raise HTTPException(404, detail=f"發生錯誤！錯誤內容：{e}")

    context = {
        "request": request,
        "game": game,
        "discord_id": discord_id,
        "gt": gt,
        "challenge": challenge,
    }
    logging.info(context)
    return templates.TemplateResponse("index.html", context)


@app.post("/geetest/{game}/{discord_id}", response_class=PlainTextResponse)
async def save_geetest_result(
    game: Literal["genshin", "starrail_battlechronicle"],
    discord_id: int,
    result: GeetestResult,
):
    """使用者通過圖形驗證後頁面請求本路徑，儲存結果資料"""
    logging.info(f"{type(discord_id)} {result.dict()}")
    user = await Database.select_one(User, User.discord_id.is_(discord_id))
    if user is None:
        return "使用者不存在資料庫內，請先設定 Cookie 註冊使用者"
    match game:
        case "genshin":
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
        case "starrail_battlechronicle":
            cookie = user.cookie_starrail or user.cookie_default
            client = genshin.Client(
                cookie,
                lang="zh-tw",
                game=genshin.Game.STARRAIL,
                region=genshin.Region.OVERSEAS,
                proxy=os.getenv("PROXY_SERVER"),
            )
            mmt_result = genshin.models.auth.geetest.MMTResult(
                geetest_challenge=result.geetest_challenge,
                geetest_validate=result.geetest_validate,
                geetest_seccode=result.geetest_seccode,
            )
            try:
                await client.verify_mmt(mmt_result)
                return "圖形驗證成功！可以回到小幫手繼續使用指令"
            except Exception as e:
                return f"發生錯誤！你可以嘗試重新整理網頁重試，錯誤內容：{e}"


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """所有 HTTP 錯誤導向此頁面"""
    context = {"request": request, "error": exc.detail}
    return templates.TemplateResponse("error.html", context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
