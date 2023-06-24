FROM python:latest

ENV PYTHONUNBUFFERED 1
ENV PORT 8080
ENV PYTHONPATH=/app
ENV API_ROOT=$API_ROOT
WORKDIR app/


COPY . ./
RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

CMD python photokiosk_nicegui/main.py

EXPOSE 8080