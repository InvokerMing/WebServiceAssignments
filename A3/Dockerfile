FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/

COPY start.sh /start.sh
RUN chmod +x /start.sh
RUN mkdir -p /data

EXPOSE 5000
EXPOSE 5001

CMD ["/start.sh"]