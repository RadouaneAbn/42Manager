#!/bin/bash

date +%s > ~/.lock_time
ft_lock
/home/rabounou/dev/log-manager/main.py
rm ~/.lock_time