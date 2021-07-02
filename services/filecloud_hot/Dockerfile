FROM python:3.8.0-alpine
WORKDIR /app
#ADD . /app

EXPOSE 5000
#ENV FLASK_APP=filecloud_hot.py

RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
COPY ./requirements.txt /app/requirements.txt
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && apk add postgresql-dev gcc python3-dev musl-dev \
  && apk add --no-cache file-dev gcc \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies
#RUN pip install filemagic

COPY . /app
#ENTRYPOINT [ "flask"]
#CMD ["run", "-h", "0.0.0.0", "-p", "5000"]
# "-mount source=TEST_volume", "destination="]