#! /bin/bash

TIMESTAMP=$(date +'%d-%m-%Y_%H-%M')

current_time=$(date +'%d-%m-%Y %H:%M:%S')

./modules/alert "Recon started at $current_time, results will be sent to you shortly ⏳"

for org_name in $(cat orgs.txt); do
  cd $org_name

  for domain in $(cat domains.txt); do
    mkdir -p $TIMESTAMP/$domain
    cd $TIMESTAMP/$domain

    echo "[+] Running subfinder on $domain"
    subfinder -d $domain -o subdomains.txt
    clear

    if [ $(wc -l subdomains.txt | awk '{print $1}') -gt 10000 ]; then
      echo "[-] Skipping httpx on $domain as subdomains are more than 10k"
      continue
    fi

    echo "[+] Running httpx on $domain"
    httpxx -l subdomains.txt -o alive.txt -no-color
    clear
    httpxx -l subdomains.txt -o info.txt -status-code -title -web-server -ip -cname -rl 10 -no-color -follow-redirects

    ../../../modules/sendfile subdomains.txt $domain
    ../../../modules/sendfile info.txt $domain
    ../../../modules/sendfile alive.txt $domain

    clear
    cd ../../
  done
done
