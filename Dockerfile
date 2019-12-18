FROM python:3.6.4
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean
RUN apt-get install -y \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    net-tools \
    vim

RUN mkdir /src
WORKDIR /src
ADD ./src /src
RUN pip install -r requirements.pip

EXPOSE 9091
STOPSIGNAL SIGINT

CMD python ./manage.py migrate --settings=car_pooling.settings.local; python ./manage.py runserver 0.0.0.0:9091 --settings=car_pooling.settings.local