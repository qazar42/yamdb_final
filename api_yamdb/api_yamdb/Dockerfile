FROM python:3.7-slim

WORKDIR /app

COPY ../requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ../api_yamdb/ .

LABEL author='qazar42' version=3 broken_keyboards=1

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 
