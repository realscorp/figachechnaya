FROM python:3.8.10
WORKDIR /code
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    python3-tk=3.8.10* \
    && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app/main.py /code/
CMD ["python3", "main.py"]