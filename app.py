from flask import Flask, request, abort
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import *
import os, stock, configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read("config.ini")

# Channel Access Token
line_bot_api = LineBotApi(config["LINE"]["ACCESS_TOKEN"])
# Channel Secret
handler = WebhookHandler(config["LINE"]["SECRET"])

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=["POST"])
def callback():
	# get X-Line-Signature header value
	signature = request.headers["X-Line-Signature"]
	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)
	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return "OK"

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	if event.message.text.startswith("#"):
		stockNO = event.message.text[1:]
		rTInfo = stock.stockRT(stockNO) #Real Time info
		message = TextSendMessage(rTInfo)
	elif event.message.text.startswith("/"):
		stockNO = event.message.text[1:]
		rTInfo = stock.monthP(stockNO)
		message = ImageSendMessage(original_content_url = rTInfo,
								   preview_image_url = rTInfo)
	elif (event.message.text.lower() == "help"):
		help_log = "輸入'#+股票代號'來查詢即時股價\n輸入'/+股票代號'以顯示一個月內股價走向"
		message = TextSendMessage(help_log)
	else:
		invalidSentence = "無法辨識的內容，輸入[help]獲得更多資訊"
		message = TextSendMessage(invalidSentence)
	line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)