# Laffka
>Opensource torshop application written in Python 3, and powered by Flask.
1. [ Introduction ](#introduction)
2. [ Installation ](#installation)

<a name="introduction"></a>
## Introduction
Application was developed with hidden service in mind after realisation, that customers cant withdraw money from [Valhalla market](valhallaxmn3fydu.onion), only vendors can.

I think this is very unfriendly, and I deem hiddenservice market places as a dumb idea at all. Centralized drug selling place, honeypot for LEOs. And exitscams.

Many would do perfectly fine with own small shop hidden somewhere in __onion land.__

Well, here it is, my solution - **Laffka**. Most important Laffkas feature is that one doesnt need daemons or blockchain to receive payments.

Payments go to the publcic bitcoin addresses, while private keys are stored in sqlite database, and can be later sweeped from any selfrespectable bitcoin wallet there are.

Bitcoin public and private addresses are generated from mnemonics in [__/app/config.py__ ](app/configuration.py),Remember, you HAVE to edit this file in order to run Laffka.


<a name="#installation"></a>
## Installation

Requirements - [**python3**](https://www.python.org/download/releases/3.0/), might work on Windows machine uses cron in the same way, never checked, why bother.

From own experience can say, that installing on **Centos 7.4** provided by [Evolution Host] (https://evolution-host.com/) takes under 15 minutes.

1. ```yum -y install git``` we require git to clone Laffka on filesystem.
2. ```yum -y install https://centos7.iuscommunity.org/ius-release.rpm``` we need to install IUS for **Python3**
3. ```yum -y install python36u``` we need. or at least I have used **3.6** Python
4. ```yum -y install python36u-pip``` and finally we need **pip** for aquired python.
5. ```git clone https://github.com/eruina/laffka.git``` we need clone **Laffka** in order to use it, of course.
6. ```cd laffka```
7. ```pip3.6 install -r requirements.txt``` for Laffka, we need next python packages: [requests](http://docs.python-requests.org/en/master/),[Flask](http://flask.pocoo.org/),[Flask-APScheduler](https://github.com/viniciuschiele/flask-apscheduler), [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/), [bitmerchant](https://github.com/sbuss/bitmerchant),[Flask-Login](https://flask-login.readthedocs.io/en/latest/), [Flask-Session](https://pythonhosted.org/Flask-Session/), [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/)
