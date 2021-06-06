FROM python:3.8.0-alpine
WORKDIR /app
ADD . /app

EXPOSE 5000
ENV FLASK_APP=filecloud_app.py

RUN apk --update add python py-pip openssl ca-certificates py-openssl wget
RUN apk --update add --virtual build-dependencies libffi-dev openssl-dev python-dev py-pip build-base \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && apk del build-dependencies

ENTRYPOINT [ "flask"]
CMD ["run", "-h", "0.0.0.0", "-p", "5000"]
# "-mount source=TEST_volume", "destination="]