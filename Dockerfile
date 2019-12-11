# This Dockercontainer is only relevant for development purposes atm

FROM debian:buster
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update; apt-get -y install python3-psycopg2 python3-autopep8 python3-pytest-cov python3-pytest git postgresql

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/workspaces/pg_sequence_to_identity"

COPY . .
CMD ["bash","entrypoint.sh"]


