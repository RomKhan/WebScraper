FROM python:3.9

RUN echo "deb http://deb.debian.org/debian/ sid main" >> /etc/apt/sources.list \
  && apt-get update -qqy \
  # && apt-get -qqy install chromium=89.0.4389.82-1 \
  # && apt-get -qqy install chromium=90.0.4430.212-1 \
  # && apt-get -qqy install chromium=93.0.4577.82-1 \
  # && apt-get -qqy install chromium=97.0.4692.71-0.1 \
  # && apt-get -qqy install chromium=98.0.4758.102-1+b1 \
  && apt-get -qqy install chromium \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# install chromedriver, which will be located at /usr/bin/chromedriver
RUN apt-get update -qqy \
  && apt-get -qqy install chromium-driver \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

#... (install dependencies)

COPY ./shallow_sale_parser/start.py /app/
COPY ./shallow_sale_parser/utils.py /app/
COPY ./shallow_sale_parser/parsers /app/parsers/

COPY ./shallow_sale_parser/requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./abstract /app/abstract/
RUN pip install -r app//abstract/requirements.txt

#COPY ./undetected_chromedriver /app/undetected_chromedriver/

# Create the necessary directories for copying the binary
RUN mkdir -p /var/chromedriver/

# copy the chromedriver binary, so that it can be patched by undetected_chromedriver
RUN cp /usr/bin/chromedriver /var/chromedriver/chromedriver_copy

WORKDIR /app
CMD ["python", "start.py"]