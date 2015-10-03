# Steam Game Chooser

Source code for [steamgamechooser.com](http://steamgamechooser.com).
Chooses Steam games for you to play.

Written with [Bottle](http://bottlepy.org/) and [Vanilla JS](http://vanilla-js.com/).


## Absolute minimal setup requirements

Install the requirements to your environment ([Virtualenv](https://virtualenv.pypa.io) highly recommended). If you're not using Virtualenv, might require root/sudo.

```
pip install -r requirements.txt
```

Get yourself a Steam API key from [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey) and save it in `settings.py`.

Run the app:

```
python run.py
```


## Slightly better setup

This will of course also need you to complete the absolute minimal setup first.

Make sure any horrendous web servers left over by the default install are removed.

```
systemctl stop httpd
systemctl disable httpd
```

Next up, install gcc, git, nginx, uwsgi, virtualenv and all the good things (e.g. dependencies of some requirements).
If you're on CentOS this generally means:

```
sudo yum install -y epel-release
sudo yum install -y git nginx uwsgi libxml2 libxml2-devel libxslt-devel python-virtualenv uwsgi-plugin-python
```

Create a user for SGC, and make sure Nginx is in the same group. In CentOS that would be e.g.:

```
adduser sgc
usermod -a -G sgc nginx
```

Get the code and set up requirements in a Virtualenv.

```
su - sgc
chmod g+x ~
git clone https://github.com/lietu/sgc.git
cd sgc
virtualenv .virtualenv
source .virtualenv/bin/activate
pip install -r requirements.txt
mkdir cache
```

Set up the app in uWSGI from `server/` (as root, and remember to check app.ini contents):

```
cp server/uwsgi.ini /etc/uwsgi.ini
service uwsgi restart
```

Set up Nginx configuration from `server/` (as root, check that user, etc. match your environment, e.g. on Debian based systems user should probably be www-data).

```
cp server/nginx.conf /etc/nginx
cp server/site.conf /etc/nginx/conf.d/
nginx -t
service nginx restart
```

Don't forget to open your firewall, e.g. in CentOS 7:

```
yum remove -y firewalld iptables
yum install -y firewalld
service firewalld enable
service firewalld start
firewall-cmd --add-service=http
```
