FROM python:3

# TODO
## bad idea?
######RUN groupadd -g 999 appuser && useradd -r -u 999 -g appuser appuser
#####USER appuser
#https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b

WORKDIR /home/croeder/harmonization_ui


# Install Python Packages
ADD requirements.txt /home/croeder/harmonization_ui
RUN pip install -r requirements.txt


# Install PostgreSQL Client
RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' >> /etc/apt/sources.list.d/pgdg.list
RUN apt-get update
RUN wget --no-check-certificate -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O- | apt-key add -
RUN apt-get install -y --allow-unauthenticated postgresql-client-9.6 # TODO


# misc
RUN apt-get update
RUN apt-get install -y lsof
RUN apt-get install -y vim


# dev, the app 
EXPOSE 8000

RUN mkdir /home/croeder/harmonization_ui/django_harmonization
COPY django_harmonization  /home/croeder/harmonization_ui/django_harmonization/django_harmonization

COPY backups /home/croeder/harmonization_ui/django_harmonization/backups
COPY bin /home/croeder/harmonization_ui/django_harmonization/bin
COPY ddl /home/croeder/harmonization_ui/django_harmonization/ddl
COPY r_lang /home/croeder/harmonization_ui/django_harmonization/r_lang
COPY sql /home/croeder/harmonization_ui/django_harmonization/sql

WORKDIR /home/croeder/harmonization_ui/django_harmonization/django_harmonization
CMD ["pwd"]
CMD ["ls"]
CMD ["./docker-entrypoint.sh"]



# notes:
# docker build -t harmonization_ui 
# docker run --env-file env.list -p 8010:8000 harmonization_ui
# docker container ls 
# docker exec -it <id> /bin/bash
# docker container stop <id>


