# Hoyolab-Geetest-Webserver

本專案是給 [原神小幫手 Discord 機器人](https://github.com/KT-Yeh/Genshin-Discord-Bot) 作為讓使用者設定 Geetest 圖形驗證的網頁伺服器，因此本專案內會連動操作原神小幫手的資料庫，若需要開發測試，請先移除與資料庫有關的程式碼

### 流程
1. 原神小幫手端
    1. 觸發 hoyolab 要求驗證，收到 hoyolab 發送的 `gt`、`challenge`
    2. 產生連結讓使用者連到此 web server
2. 本程式
    1. 透過 URL GET 路徑接收使用者 `discord_id`、`gt`、`challenge`
    2. 產生網頁回傳給使用者，網頁 JavaScript 啟動圖形驗證
    3. 使用者解鎖圖形驗證後，geetest 伺服器會回傳 `challenge`、`validate`、`seccode`
    4. 將 2.3. 三個資料透過 POST 請求本程式，本程式接收後儲存至資料庫內
