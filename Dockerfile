# This Dockercontainer is only relevant for development purposes atm

FROM debian:buster
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update; apt-get -y install python3-psycopg2 python3-autopep8 python3-pytest-cov python3-pytest git


ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/workspaces/pg_sequence_to_identity/pg_sequence_to_identity:${PATH}"
