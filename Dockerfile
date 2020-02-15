FROM python:3

LABEL author="Jones Maxime Murphy III <jones.murphy@onsight.ga>"

WORKDIR /usr/src/flask/https

COPY . .

RUN pip install .

ENTRYPOINT [ "sentimental" ]

EXPOSE 443
