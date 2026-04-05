FROM python:3.14-slim

# ---- View logs terminal 
ENV PYTHONUNBUFFERED=1

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app/backend

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    # ---- Pillow
    libjpeg-dev \
    zlib1g-dev \
    # ---- del cache, after installation
    && rm -rf /var/lib/apt/lists/*


# ---- Copies only requirements.txt not all code
COPY backend/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# ---- Copies the entire project code to /app
COPY backend/ .

COPY backend/entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/backend/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "comment_board.asgi:application"]