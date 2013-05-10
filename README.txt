prototype implementation to proxy a site


install:

mkvirtualenv proxy
pip install -r requirements.txt



run:

/Django based/
python manage.py runserver

http://localhost:8000
http://localhost:8000/tunnel/https://github.com



/Twisted based/
python proxy_twisted.py

http://localhost:8880
http://localhost:8880/tunnel/https://github.com
