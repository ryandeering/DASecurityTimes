import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from influxdb_client import InfluxDBClient
from io import BytesIO
from credentials import INFLUXDB_URL, INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN

def init_influxdb_client():
    return InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def fetch_data(client):
    query_api = client.query_api()
    query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -24h) |> filter(fn: (r) => r._measurement == "terminals")'
    return query_api.query(org=INFLUXDB_ORG, query=query)

def prepare_dataframe(result):
    records = []

    for table in result:
        for record in table.records:
            record_data = {
                "_time": record.get_time(),
                "_value": record.get_value(),
                "_field": record.get_field(),
            }
            records.append(record_data)

    df = pd.DataFrame(records)

    if not df.empty:
        df["time"] = pd.to_datetime(df["_time"])
        df.rename(
            columns={"_field": "terminal", "_value": "time_duration"}, inplace=True
        )

    return df

def plot_data(df, titlename):
    matplotlib.rcParams["timezone"] = "Europe/Dublin"
    sns.set(style="darkgrid", context="talk")
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 8))

    terminal_colors = {"T1": "magenta", "T2": "cyan"}

    for terminal, color in terminal_colors.items():
        terminal_data = df[df["terminal"] == terminal]
        if not terminal_data.empty:
            ax.plot(
                terminal_data["time"],
                terminal_data["time_duration"],
                label=f"{terminal}",
                linewidth=3,
                color=color,
            )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_yticks(np.arange(5, 65, 5))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_title(titlename)
    ax.legend()
    plt.tight_layout()

    return fig

def save_plot_to_buffer(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf

def show_plot(titlename):
    client = init_influxdb_client()
    try:
        result = fetch_data(client)
        df = prepare_dataframe(result)
        if df.empty:
            return None
        fig = plot_data(df, titlename)
        plot_buffer = save_plot_to_buffer(fig)
        return plot_buffer
    finally:
        client.close()
