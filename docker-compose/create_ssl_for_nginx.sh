#!/bin/bash
mkdir -p ./ssl
openssl req -x509 \
            -nodes \
            -days 365 \
            -newkey rsa:2048 \
            -keyout ssl/ingress.key \
            -out ssl/ingress.crt \
            -subj "/subjectAltName=DNS:figachechnaya.ru"