# Базовый образ Python
FROM python:3.9

# Установка зависимостей OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

    # Установка зависимостей
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Копирование исходного кода
COPY ./app /app
#COPY ./KeysEnum.py /app

# Запуск приложения Flask
WORKDIR /app
EXPOSE 8080
#CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "--access-logfile", "-", "app:app"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]