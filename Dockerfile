FROM python:3.5
ENV PYTHONUNBUFFERED 1

# Make directory for application
WORKDIR /app
# Copy application to container
COPY . .

# Install packages
RUN pip install -r requirements.txt

# Root, media_root app folder 
VOLUME ["/app", "/media_root"]
# Expose default django port
EXPOSE 8000

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
