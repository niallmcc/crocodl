FROM python:3.8

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH /usr/src/app
CMD [ "python", "-m", "crocodl.image.web.app", "--port", "9099", "--host", "0.0.0.0", "--noclient" ]
