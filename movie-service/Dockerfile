FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /app

COPY ./movie-service/requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apt-get purge -y build-essential python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip

COPY ./movie-service/ /app/

EXPOSE 8000

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]