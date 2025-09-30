FROM python:3.9-slim-buster

WORKDIR /app

COPY /back /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]