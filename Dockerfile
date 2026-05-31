FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY static/ ./static/

# Ensure placeholder images exist if static/ was not committed yet
RUN python -c "\
from pathlib import Path; \
p = Path('static'); p.mkdir(exist_ok=True); \
jpeg = bytes([0xFF,0xD8,0xFF,0xDA,0x00,0x0C,0x01,0x01,0x00,0x01,0x3F,0x00,0xFF,0xD9]); \
[f.write_bytes(jpeg) for f in [p/'catalog.jpg', p/'wholesale.jpg', p/'price_list.jpg'] if not f.exists()] \
"

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
