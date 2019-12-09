FROM python:3.7-alpine
MAINTAINER max shah
LABEL version=3.7-alpine
WORKDIR /code
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0
COPY . .
RUN pip install -r requirements.txt
CMD ["flask", "run"]
