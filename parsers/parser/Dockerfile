FROM python:3.9

RUN echo "deb http://deb.debian.org/debian/ sid main" >> /etc/apt/sources.list \
  && apt-get update -qqy \
  && apt-get -qqy install chromium \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# install chromedriver, which will be located at /usr/bin/chromedriver
RUN apt-get update -qqy \
  && apt-get -qqy install chromium-driver \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#... (install dependencies)

COPY ./parser/start.py /app/
COPY ./parser/utils.py /app/
COPY ./parser/shallow_parsers /app/shallow_parsers/
COPY ./parser/deep_parsers /app/deep_parsers/

COPY ./parser/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./abstract /app/abstract/
RUN pip install -r app//abstract/requirements.txt

COPY ./KeysEnum.py /app

# Create the necessary directories for copying the binary
RUN mkdir -p /var/chromedriver/

# copy the chromedriver binary, so that it can be patched by undetected_chromedriver
RUN cp /usr/bin/chromedriver /var/chromedriver/chromedriver_copy
#ARG WEBSITE_NAME=циан
#ARG CITY=Москва
#ENV WEBSITE_NAME=${WEBSITE_NAME}
#ENV CITY=${CITY}

WORKDIR /app
CMD ["python", "start.py"]