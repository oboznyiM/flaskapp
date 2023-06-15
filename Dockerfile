FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
ENV FLASK_APP=server.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
