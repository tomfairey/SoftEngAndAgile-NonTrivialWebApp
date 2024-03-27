# FROM python:3.11-alpine
FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./main.py /code/
COPY ./app/ /code/app/

EXPOSE 80

CMD ["python", "main.py"]
