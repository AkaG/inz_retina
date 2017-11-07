FROM python:3.5
ENV PYTHONUNBUFFERED 1

# Make directory for application
WORKDIR /app
# Copy application to container
COPY . .

# Install django
RUN pip install --no-cache-dir django \
            djangorestframework \
            django-extensions \
            django-cleanup \
            Pillow

# Install postgresql driver
RUN pip install --no-cache-dir psycopg2

# Install Tensorflow CPU
RUN pip install --no-cache-dir tensorflow

# Install Keras
RUN pip install --no-cache-dir keras

# Install other packages
RUN pip install --no-cache-dir h5py
RUN pip install --no-cache-dir scikit-image

# Root, media_root app folder 
VOLUME ["/app", "/media_root"]
# Expose default django port
EXPOSE 8000

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
