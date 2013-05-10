prototype implementation to proxy a site


install:

mkvirtualenv proxy
pip install -r requirements.txt



run:

/Django based/
python manage.py runserver

<a href="http://localhost:8000">http://localhost:8000</a>
<a href="http://localhost:8000/tunnel/https://github.com">http://localhost:8000/tunnel/https://github.com</a>



/Twisted based/
python proxy_twisted.py

<a href="http://localhost:8880">http://localhost:8880</a>
<a href="http://localhost:8880/tunnel/https://github.com">http://localhost:8880/tunnel/https://github.com</a>
