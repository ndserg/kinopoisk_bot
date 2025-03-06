FROM python:3.12.9-slim-bookworm

RUN apt-get update && apt-get install -y locales-all && apt-get install --reinstall ca-certificates

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]

CMD []
