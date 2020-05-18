FROM python:3.8-alpine
COPY . .
RUN apk add gcc libc-dev libxml2-dev libxml2 libxslt-dev python3-dev && pip install -r requirements.txt
CMD python3 app.py
