FROM alpine:3.2

RUN echo "http://dl-4.alpinelinux.org/alpine/edge/community/" >> /etc/apk/repositories && \
    apk add --update bash python3 py-pip && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/*


RUN mkdir -p /opt/pretenders/

ADD requirements /opt/pretenders/requirements

RUN pip install -r /opt/pretenders/requirements/runtime.txt

ADD pretenders /opt/pretenders/pretenders

EXPOSE 8000
ENV PYTHONPATH=/opt/pretenders

CMD python -m pretenders.server.server --host 0.0.0.0 --port 8000
