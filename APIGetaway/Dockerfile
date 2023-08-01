# Базовый образ Python
FROM python:3.9

# Установка зависимостей
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Копирование исходного кода
COPY ./APIGetaway.py /app/APIGetaway.py

ENV FLASK_APP=APIGetaway.py

# Запуск приложения Flask
WORKDIR /app
EXPOSE 8083
CMD ["uvicorn", "APIGetaway:app", "--host", "0.0.0.0", "--port", "8083", "--workers", "2"]