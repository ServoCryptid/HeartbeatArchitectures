#!/bin/bash

VMS=2

CENTRALISED=0
RING=1
ALL_TO_ALL=0

gcloud config set compute/zone us-central1-a

for i in $(seq 0 $VMS)
  do
    gcloud compute ssh instance-$i -- sudo systemctl stop my_\* #stop my services if running
  done


for i in $(seq 0 $VMS)
  do
    gcloud compute ssh instance-$i -- mkdir -p /tmp/DS1/
    gcloud compute scp server_list.txt *.py *.service instance-$i:/tmp/DS1/

    gcloud compute ssh instance-$i -- sudo cp /tmp/DS1/*.service /etc/systemd/system/ # move files to required path
    gcloud compute ssh instance-$i -- sudo cp /tmp/DS1/*.py /usr/local/bin/ # move the files to the desired location without having to use sudo

    if [ "1" -eq "$CENTRALISED" ]; then
      gcloud compute ssh instance-$i -- sudo systemctl daemon-reload # reload system files in systemd

      if [ "0" -eq "$i" ]; then # in this case, instance 0 will be the server
        gcloud compute ssh instance-$i -- sudo systemctl restart my_server.service
      else
        gcloud compute ssh instance-$i -- sed -n "1"p /tmp/DS1/server_list.txt > servers.txt #save in a .txt files
                                                                                  # the servers list for the clients
        gcloud compute scp servers.txt instance-$i:/tmp/DS1/
        gcloud compute ssh instance-$i -- sudo mv /tmp/DS1/servers.txt /usr/local/bin/
        rm servers.txt
        gcloud compute ssh instance-$i -- sudo systemctl restart my_client.service
      fi

    elif [ $RING -eq "1" ]; then
      client=$i
      server=$(($(($i+1))%$(($VMS+1))))

      gcloud compute ssh instance-$i -- sudo systemctl daemon-reload # reload system files in systemd
      gcloud compute ssh instance-$server -- sudo systemctl restart my_server.service

      gcloud compute ssh instance-$client -- sed -n "$(($server+1))"p /tmp/DS1/server_list.txt > servers.txt
      gcloud compute scp servers.txt instance-$i:/tmp/DS1/
      gcloud compute ssh instance-$i -- sudo mv /tmp/DS1/servers.txt /usr/local/bin/
      rm servers.txt

      gcloud compute ssh instance-$client -- sudo systemctl restart my_client.service

    elif [ $ALL_TO_ALL -eq "1" ]; then
      gcloud compute ssh instance-$i -- sudo systemctl daemon-reload # reload system files in systemd
      gcloud compute ssh instance-$i -- sed -n "$(($i+1))d;p" /tmp/DS1/server_list.txt > servers.txt #each instances sends to everyone
      gcloud compute scp servers.txt instance-$i:/tmp/DS1/
      gcloud compute ssh instance-$i -- sudo mv /tmp/DS1/servers.txt /usr/local/bin/
      rm servers.txt

      gcloud compute ssh instance-$i -- sudo systemctl restart my_server.service
      gcloud compute ssh instance-$i -- sudo systemctl restart my_client.service

    fi
  done