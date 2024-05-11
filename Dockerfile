FROM rockylinux:9

MAINTAINER Nick Zolotarov <n.zolot@hotmail.com>

ARG VERSION=1.27
ENV APP_HOME    /app
ENV RUN_USER    app
ENV RUN_GROUP   app

RUN yum -y install pip

COPY requirements/requirements-${VERSION}.txt $APP_HOME/requirements.txt
RUN groupadd -g 4332 $RUN_GROUP && \
    useradd -u 4332 -g $RUN_GROUP $RUN_USER && \
    chown $RUN_USER:$RUN_GROUP $APP_HOME -R

WORKDIR $APP_HOME
USER $RUN_USER
RUN pip install -r requirements.txt

COPY package $APP_HOME

ENTRYPOINT ["python3", "main.py"]
