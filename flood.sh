#!/bin/sh

processes=$(pgrep -c hping3);

if [ $processes -gt 1 ] 
then 
	sudo pkill hping3
fi
