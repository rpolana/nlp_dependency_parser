FROM python:3.6-slim-buster

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    ca-certificates \
    dos2unix \
    nginx \
    unzip \
    wget \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

RUN ln -sf /usr/local/bin/python3.6 /usr/bin/python \
    && ln -sf /usr/local//bin/python3.6 /usr/bin/python3 \
    && ln -s /usr/local//bin/pip3 /usr/bin/pip

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN pip install --upgrade pip
RUN echo "Installing pytorch ..." && \
    pip install torch==1.10.1+cpu -f https://download.pytorch.org/whl/torch_stable.html && \
    echo "Installed pytorch"

COPY ./requirements.txt /opt/app/requirements.txt
RUN echo "Installing python requirements ..." && \
    pip install -r /opt/app/requirements.txt && \
    echo "Installed python requirements."


RUN pip install gunicorn gevent==20.04.0

# COPY ./source /opt/app
# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/bin:${PATH}"
ENV PATH /opt/app:$PATH
ENV NLTK_DATA /opt/app/nltk_data/
# ADD ./nltk_data $NLTK_DATA

# EXPOSE 5000/tcp
COPY docker_entrypoint.sh /opt/bin/entrypoint.sh
RUN chmod 755 /opt/bin/entrypoint.sh
WORKDIR /opt/bin

# CMD  "/usr/bin/python /opt/app/wsgi.py" ; /bin/bash -C "sleep infinity"
ENTRYPOINT ["/opt/bin/entrypoint.sh"]
