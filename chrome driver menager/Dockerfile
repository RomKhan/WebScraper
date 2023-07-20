# Базовый образ Python
FROM python:3.9

RUN echo "deb http://deb.debian.org/debian/ sid main" >> /etc/apt/sources.list \
  && apt-get update -qqy \
  && apt-get -qqy install chromium \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# install chromedriver, which will be located at /usr/bin/chromedriver
RUN apt-get update -qqy \
  && apt-get -qqy install chromium-driver \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

    # Установка зависимостей
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Копирование исходного кода
COPY ./chrome_server.py /app/chrome_server.py

ENV FLASK_APP=chrome_server.py

# Create the necessary directories for copying the binary
RUN mkdir -p /var/chromedriver/
ENV CHROMEDRIVER_PATH=/var/chromedriver/chromedriver_copy
# copy the chromedriver binary, so that it can be patched by undetected_chromedriver
RUN cp /usr/bin/chromedriver /var/chromedriver/chromedriver_copy

# Запуск приложения Flask
WORKDIR /app
EXPOSE 8082
CMD ["waitress-serve", "--host", "0.0.0.0", "--port", "8082", "chrome_server:app"]