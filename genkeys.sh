#!/bin/sh
mkdir -p keys
openssl genrsa -out keys/server.key 4096
openssl req -new -key keys/server.key -out keys/server.csr
openssl x509 -req -in keys/server.csr -signkey keys/server.key -out keys/server.crt
