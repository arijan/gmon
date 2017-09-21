#!/bin/sh
gunicorn \
	--bind  0.0.0.0:8081 \
	--reload \
	--timeout 90 \
	-k gevent \
	--log-level info \
	--access-logfile access.log \
	--error-logfile error.log \
	--capture-output \
	web:default_app

