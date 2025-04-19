FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /app

EXPOSE 8000

COPY . /app

RUN pip install -r requirements.txt

CMD ["fastapi", "run", "src/api.py", "--host", "0.0.0.0", "--port", "8000"]