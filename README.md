# Dublin Airport Security Times

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/ryandeering/DASecurityTimes/actions)

A project born from frustration with Dublin Airport bottlenecking in the summer of 2022, I created a public Twitter bot so that people can easily assess how long they should give themselves to get through airport security, as well as to give an idea of how busy the airport is. 

I am not naturally a Python developer, only using the language really for little scripts, data analytics and working with Tensorflow. But certain libraries like Tweepy, BeautifulSoup and Matplotlib seemed like a logical choice for using it with this project. It was also a great excuse to get more familiar with it from a networking and I/O point of view. So, if you see anything you might consider not too 'Pythonic' or just bad practice, let me know!

The project is set up to post on Twitter every 30 minutes, inserting into an InfluxDB measurement everytime it does so. It also posts a chart using Matplotlib twice a day, at midnight and midday, of the previous 24 hours of activity. It has now has a BlueSky version. This can be seen below.

The bot accumulated 1,000 followers in it's first week of existence!

[Link to Twitter Bot](https://twitter.com/DASecurityTimes)
[Link to BlueSky Bot](https://bsky.app/profile/dasecuritytimes.bsky.social)

<h1> Built With </h1>

* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - For data scraping from Dublin Airport website
* [InfluxDB](https://docs.influxdata.com/influxdb/v1.8/) - OSS time-series database, for storing security times
* Numpy, Pandas, Matplotlib, Seaborn - For data analytics and creation of chart
* [Tweepy](https://www.tweepy.org/) - Python library to call Twitter API
* [Pillow](https://pillow.readthedocs.io/en/stable/) - Python image library
* [ATProto](https://atproto.blue/en/latest/) - ATProto SDK, underlying decentralised network behind BlueSky

![image](https://user-images.githubusercontent.com/37181720/174308996-703472b3-58af-4412-9573-d0c0225dc62e.png)
