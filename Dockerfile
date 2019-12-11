# This Dockercontainer is only relevant for development purposes atm

FROM debian:buster
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update; apt-get -y install lsb-release curl ca-certificates gnupg; apt-get clean
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update; apt-get -y install python3-psycopg2 python3-autopep8 python3-pytest-cov python3-pytest git postgresql-12 ; apt-get clean

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/workspaces/pg_sequence_to_identity"

COPY . .
CMD ["bash","entrypoint.sh"]


