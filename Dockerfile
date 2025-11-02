FROM python:3.13.7-slim

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "main.py" ]