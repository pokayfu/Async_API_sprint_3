FROM python:3.10-slim
WORKDIR /tests
COPY requirements.txt /tests/
RUN pip install -r requirements.txt
RUN python -m pip install --upgrade pip setuptools
RUN apt-get update && apt-get install -y netcat-openbsd
COPY . /tests/
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
CMD ["pytest", "tests/unit", "-p", "no:warnings"]
