#!/usr/bin/env bash

cd inz_retina
git pull origin master
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d