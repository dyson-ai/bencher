#! /bin/bash

rocker --x11 --user --home --pull --name mycont ubuntu:22.04 & ./code-remove-container .