from datetime import timedelta, datetime
from imgurpython import ImgurClient
from matplotlib.font_manager import FontProperties
import twstock, time, matplotlib, configparser
import matplotlib.pyplot as plt
import pandas as pd
#fontprop = FontProperties(fname = ".fonts/DejaVuSans.ttf")

matplotlib.use("Agg")

config = configparser.ConfigParser()
config.read("config.ini")

def uploadFig(fig):
	client_id = config["IMGUR"]["CLIENT_ID"]
	client_secret = config["IMGUR"]["CLIENT_SECRET"]
	client = ImgurClient(client_id, client_secret)
	#print("Uploading image... ")
	image = client.upload_from_path(fig, anon=True)
	#print("Done")
	return image["link"]

def stockRT(Snum): #Stock Number
	respon = ""
	stock_rt = twstock.realtime.get(Snum)
	cur_datetime = datetime.fromtimestamp(stock_rt["timestamp"]+8*60*60)
	cur_time = cur_datetime.strftime("%H:%M:%S")
	respon += "%s (%s) %s\n"%(stock_rt["info"]["name"],
							   stock_rt["info"]["code"],
							   cur_time)
	respon += "現價: %s / 開盤: %s\n"%(stock_rt["realtime"]["latest_trade_price"],
									   stock_rt["realtime"]["open"])
	respon += "最高: %s / 最低: %s\n"%(stock_rt["realtime"]["high"],
									   stock_rt["realtime"]["low"])
	respon += "量: %s\n" %(stock_rt["realtime"]["accumulate_trade_volume"])
	#stock = twstock.Stock("2330")
	stock = twstock.Stock(Snum)
	respon += "-----\n"
	respon += "最近五日價格: \n"
	price5 = stock.price[-5:][::-1]
	date5 = stock.date[-5:][::-1]
	for i in range(len(price5)):
		respon += "[%s] %s\n" %(date5[i].strftime("%Y-%m-%d"), price5[i])
	return respon

def monthP(Snum): #month Price
	stockFig = "%s.png"%(Snum)
	stock = twstock.Stock(Snum)
	stockData = {"close":stock.close, "date":stock.date, "open":stock.open}
	df1 = pd.DataFrame.from_dict(stockData)
	df1.plot(x = "date", y = "close")
	#heroku底下中文字型會出現KeyError，待解決
	#plt.xlabel("日期", fontproperties = fontprop)
	#plt.ylabel("股價", fontproperties = fontprop)
	plt.title("[%s]" %(stock.sid))
	plt.savefig(stockFig)
	plt.close()
	respon = uploadFig(stockFig)
	return respon