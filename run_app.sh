#!/bin/bash
source /home/camilo/anaconda3/bin/activate /home/camilo/anaconda3/envs/falcon_uploader
gunicorn -c uploader_app/config.py uploader_app.app
