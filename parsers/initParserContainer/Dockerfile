FROM python:3.9

COPY ./requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY ./initConainer.py /app

WORKDIR /app
CMD ["python", "initConainer.py"]