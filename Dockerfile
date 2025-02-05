FROM python:3.8-alpine

WORKDIR /opt/pretenders
ENV PYTHONPATH=/opt/pretenders
EXPOSE 8000

RUN apk add bash
COPY requirements/ requirements/

RUN pip3 install -r /opt/pretenders/requirements/runtime.txt

COPY pretenders/ pretenders/

CMD ["python3", "-m", "pretenders.server.server", "--host", "0.0.0.0", "--port", "8000"]
