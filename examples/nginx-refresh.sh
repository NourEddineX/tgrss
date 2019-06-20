#!/bin/bash
if [ "$EUID" != "0" ]; then
	exit 1
fi
systemctl restart tgrss
systemctl restart nginx
rm -rf /data/nginx/cache/*

