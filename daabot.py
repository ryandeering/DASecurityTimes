import calendar
import re
from datetime import datetime, timedelta
from io import BytesIO

import requests
import tweepy
from bs4 import BeautifulSoup
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
from PIL import Image

from credentials import (
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    INFLUXDB_URL,
    INFLUXDB_BUCKET,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
)
from daaplot import show_plot

def init_twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def init_influxdb_client():
    return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)


def get_airport_times():
    URL = "https://www.dublinairport.com/flight-information/live-departures"
    html_doc = requests.get(URL).content
    soup = BeautifulSoup(html_doc, "html.parser")
    times = soup.find("div", class_="sec-times").findAll("strong")
    t1 = re.findall(r"\d+", times[0].getText())[0]
    t2 = re.findall(r"\d+", times[1].getText())[0]
    return t1, t2


def write_to_influxdb(influx_client, t1, t2):
    point = Point("terminals").field("T1", int(t1)).field("T2", int(t2))
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)


def generate_tweet(today, t1, t2):
    date_time = today.strftime("%d/%m/%Y %H:%M")
    tweet = f"Current times - {calendar.day_name[today.weekday()]}, {date_time} \nTerminal 1: {t1} minutes\nTerminal 2: {t2} minutes"

    if t1 == "60" or t2 == "60":
        tweet += "\n\nWARNING: Allow yourself extra time to get through security. A terminal is peaking."

    return tweet


def plot_and_upload():
    current_time = datetime.now().strftime("%H:%M")
    date = datetime.today() - timedelta(days=1)
    plot_title = None
    plot_media = None

    if current_time == "12:00":
        plot_title = (
            date.strftime("%d/%m/%Y")
            + " - "
            + datetime.today().strftime("%d/%m/%Y")
            + " Security Times"
        )
        plot_media = show_plot(plot_title)
    elif current_time == "00:00":
        plot_title = date.strftime("%d/%m/%Y") + " Security Times"
        plot_media = show_plot(plot_title)

    return plot_media

def upload_tweet(api, text, image_buffer=None):
    try:
        if image_buffer:
            image_buffer.seek(0)
            uploaded_media = api.media_upload(filename='plot.png', file=image_buffer)
            api.update_status(status=text, media_ids=[uploaded_media.media_id_string])
        else:
            api.update_status(status=text)
    except Exception as e:
        print("An error occurred while posting the tweet:", e)

def main():
    api = init_twitter_api()
    influx_client = init_influxdb_client()
    t1, t2 = get_airport_times()

    today = datetime.now()
    tweet_text = generate_tweet(today, t1, t2)

    if t1 is not None and t2 is not None:
        write_to_influxdb(influx_client, t1, t2)

    plot_media = plot_and_upload()

    upload_tweet(api, tweet_text, plot_media)


if __name__ == "__main__":
    main()
