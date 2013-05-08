prototype implementation to proxy a site


install:

mkvirtualenv proxy
pip install -r requirements.txt
python manage.py runserver



test:

http://localhost:8000
http://localhost:8000/tunnel/https://github.com
