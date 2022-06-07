# Dublin Airport Security Times

A project born from frustration with Dublin Airport bottlenecking in the summer of 2022, I created a public Twitter bot so that people can easily assess how long they should give themselves to get through airport security, as well as to give an idea of how busy the airport is. 

I am not naturally a Python developer, only using the language really for little scripts, data analytics and working with Tensorflow. But certain libraries like Tweepy, BeautifulSoup and Matplotlib seemed like a logical choice for using it with this project. It was also a great excuse to get more familiar with it from a networking and I/O point of view.

The project is set up to post on Twitter every 30 minutes, inserting into an InfluxDB measurement everytime it does so. It also posts a chart using Matplotlib twice a day, at midnight and midday, of the previous 24 hours of activity. This can be seen below.

The bot accumulated 1,000 followers in it's first week of existence!

[Link to Bot](https://twitter.com/DASecurityTimes)

Technologies:

* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - For data scraping from Dublin Airport website
* [InfluxDB](https://docs.influxdata.com/influxdb/v1.8/) - OSS time-series database, for storing security times
* Numpy, Pandas, Matplotlib, Seaborn - For data analytics and creation of chart
* [Tweepy](https://www.tweepy.org/) - Python library to call Twitter API
* [Pillow](https://pillow.readthedocs.io/en/stable/) - Python image library


![chart2](https://user-images.githubusercontent.com/37181720/172485492-19788834-6de4-4d83-8e81-cb356da64365.png)
