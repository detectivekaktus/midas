FROM python:3.13.7-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY . .
RUN useradd -m midasuser && chown -R midasuser:midasuser /app

USER midasuser

CMD [ "python3", "main.py" ]