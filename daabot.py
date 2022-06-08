import calendar
import re
from datetime import date, datetime, timedelta
from io import BytesIO
from time import sleep, strftime

import requests
import tweepy
from bs4 import BeautifulSoup
from influxdb import InfluxDBClient
from PIL import Image

from credentials import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
from daaplot import show_plot


def uploadimage():
    sleep(5)  # let i/o do it's thing
    img = Image.open("chart.png")
    b = BytesIO()
    img.save(b, "PNG")
    b.seek(0)
    ret = api.media_upload(filename="foo", file=b)  # filename doesn't matter
    return ret


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

today = datetime.now()
date_time = today.strftime("%d/%m/%Y %H:%M")

influx_client = InfluxDBClient(host="localhost", port=8086)
PLOT_SHOWN = None

URL = "https://www.dublinairport.com/flight-information/live-departures"
html_doc = requests.get(URL).content
soup = BeautifulSoup(html_doc, "html.parser")
times = soup.find("div", class_="sec-times").findAll("strong")
t1 = re.findall(r"\d+", times[0].getText())
t2 = re.findall(r"\d+", times[1].getText())

tweet = "Current times - " + calendar.day_name[today.weekday()] + ", " + date_time + " " + "\nTerminal 1: " + str(
    t1[0]) + " minutes" + "\nTerminal 2: " + str(t2[0]) + " minutes"

if t1[0] == "60" or t2[0] == "60":
    tweet += "\n\n WARNING: Allow yourself extra time to get through security. A terminal is peaking. "

if t1[0] or t2[0]:
    influx_client.write(
        ["terminals T1=" + t1[0] + ",T2=" + t2[0]], {"db": "DAA"}, 204, "line"
    )

if strftime("%H:%M") == "12:00":
    date = datetime.today() - timedelta(days=1)
    show_plot(
        date.strftime("%d/%m/%Y")
        + " - "
        + datetime.today().strftime("%d/%m/%Y")
        + " Security Times"
    )
    PLOT_SHOWN = uploadimage()
    tweet += "\n\n #DAA #DublinAirport"

if strftime("%H:%M") == "00:00":
    date = datetime.today() - timedelta(days=1)
    show_plot(date.strftime("%d/%m/%Y") + " Security Times")
    PLOT_SHOWN = uploadimage()
    tweet += "\n\n #DAA #DublinAirport"

if PLOT_SHOWN is None:
    api.update_status(tweet)
else:
    api.update_status(media_ids=[PLOT_SHOWN.media_id_string], status=tweet)
