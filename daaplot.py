import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dateutil import parser
from influxdb import InfluxDBClient


def influx_client(database=None):
    return InfluxDBClient(host="localhost", port="8086", database=database)


def show_plot(titlename):

    matplotlib.rcParams["timezone"] = "Europe/Dublin"

    result = influx_client(database="DAA").query(
        "SELECT * FROM terminals WHERE time > now()-24h"
    )

    df = pd.DataFrame(columns=["measurement", "time", "T1", "T2"])

    for k, v in result.items():
        data = {"measurement": k[0]}
        for p in v:
            data.update({"time": parser.parse(p["time"]), "T1": p["T1"], "T2": p["T2"]})
            df = df.append(data, ignore_index=True)  # convert to Pandas dataframe

    fig = plt.figure(figsize=(12, 8))

    sns.set(style="darkgrid", context="talk")
    plt.style.use("dark_background")

    plt.plot(df.time, df.T1, label="Terminal 1", linewidth=3, color="magenta")

    plt.plot(df.time, df.T2, label="Terminal 2", linewidth=3, color="cyan")

    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    y_ticks = np.arange(5, 65, 5)  # 5-60 range, ticks in 5
    plt.yticks(y_ticks)

    hours = mdates.HourLocator(interval=2)
    my_fmt = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_locator(hours)
    plt.gca().xaxis.set_major_formatter(my_fmt)

    plt.title(titlename)

    plt.legend()

    plt.tight_layout()

    plt.savefig("chart.png")
