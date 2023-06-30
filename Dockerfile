FROM python:3.10-slim-buster as Builder

WORKDIR /app

COPY . .

RUN set -xe; \
    pip3 install --upgrade pip; \
    pip3 install -r requirements.txt

FROM python:3.10-slim-buster

WORKDIR /app

COPY --from=Builder /app .
COPY --from=Builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

EXPOSE 8000

CMD ["python3", "main.py"]