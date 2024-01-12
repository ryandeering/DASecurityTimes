"""
This script automates the process of tweeting Dublin Airport security times 
and logs them in an InfluxDB database.

Written and maintained by Ryan Deering (@ryandeering)
"""

import calendar
import re
from datetime import datetime, timedelta

import requests
import tweepy
from bs4 import BeautifulSoup
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

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
    """
    Initialize and return a Tweepy API client using the provided credentials.
    """
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def init_influxdb_client():
    """
    Initialize and return an InfluxDB client with the provided credentials.
    """
    return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)


def get_airport_times():
    """
    Fetch Dublin Airport security times from the website using BeautifulSoup4 and return them.
    """
    url = "https://www.dublinairport.com/flight-information/live-departures"
    html_doc = requests.get(url, timeout=10).content
    soup = BeautifulSoup(html_doc, "html.parser")
    times = soup.find("div", class_="sec-times").findAll("strong")
    t1_minutes, t2_minutes = (
        re.findall(r"\d+", times[0].getText())[0],
        re.findall(r"\d+", times[1].getText())[0],
    )
    return t1_minutes, t2_minutes


def write_to_influxdb(influx_client, t1_minutes, t2_minutes):
    """
    Write security times to InfluxDB.
    """
    point = Point("terminals").field("T1", int(t1_minutes)).field("T2", int(t2_minutes))
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    write_api.write(bucket=INFLUXDB_BUCKET, record=point)


def generate_tweet(today, t1_minutes, t2_minutes):
    """
    Generate a tweet with security times information.
    """
    date_time = today.strftime("%d/%m/%Y %H:%M")
    tweet = (
        f"Current times - {calendar.day_name[today.weekday()]}, {date_time} \n"
        f"Terminal 1: {t1_minutes} minutes\nTerminal 2: {t2_minutes} minutes"
    )

    if t1_minutes == "60" or t2_minutes == "60":
        tweet += (
            "\n\nWARNING: Allow yourself extra time to get through security. "
            "A terminal is peaking."
        )

    return tweet


def plot_and_upload():
    """
    Generate and upload a plot with optional image to be used in the tweet -- uses daaplot.py
    """
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
    """
    Upload a tweet with optional image.
    """
    try:
        if image_buffer:
            image_buffer.seek(0)
            uploaded_media = api.media_upload(filename="plot.png", file=image_buffer)
            api.update_status(status=text, media_ids=[uploaded_media.media_id_string])
        else:
            api.update_status(status=text)
    except tweepy.TweepyException as tweep_error:
        print("An error occurred while posting the tweet:", tweep_error)


def main():
    """
    Main function to fetch security times, generate a tweet, and upload it.
    """
    api = init_twitter_api()
    influx_client = init_influxdb_client()
    t1_minutes, t2_minutes = get_airport_times()

    today = datetime.now()
    tweet_text = generate_tweet(today, t1_minutes, t2_minutes)

    if t1_minutes is not None and t2_minutes is not None:
        write_to_influxdb(influx_client, t1_minutes, t2_minutes)

    plot_media = plot_and_upload()

    upload_tweet(api, tweet_text, plot_media)


if __name__ == "__main__":
    main()
