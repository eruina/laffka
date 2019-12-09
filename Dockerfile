FROM python:alpine

RUN apk add --no-cache nano jq bash

COPY . /opt/laffka

WORKDIR /opt/laffka
RUN pip3 install -r requirements.txt

EXPOSE 5000 80 8080

CMD ["/bin/bash"]
