FROM python:3.7-alpine
MAINTAINER x0rzkov

LABEL version=3.7-alpine

ENV FLASK_APP=laffka.py \
	FLASK_RUN_HOST=0.0.0.0

RUN apk add --no-cache nano jq bash

COPY . /opt/laffka

WORKDIR /opt/laffka
RUN pip3 install -r requirements.txt

EXPOSE 5000 80 8080

CMD ["/bin/bash"]
# CMD ["flask", "run"]
