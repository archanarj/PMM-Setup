#!/bin/bash

docker --version

pmm_server_version=pmm-server-updated:2.34.0

pull_latest_image=$(docker pull xyz/percona/$pmm_server_version)

check_digests_of_image_is_not_empty=$(docker inspect xyz/percona/$pmm_server_version  --format='{{.Config.Image}}' $INSTANCE_ID)

check_if_data_volume_exists=$(docker ps -a --no-trunc --filter name=^/pmmdata$ | wc -l)

if [[ $check_digests_of_image_is_not_empty ]] && [[ $check_if_data_volume_exists < 2 ]]; then

    create_data_volume=$(docker create -v /srv --name pmmdata xyz/percona/$pmm_server_version /bin/true)
    
    source_of_image_data=$(docker inspect pmmdata | egrep "Source")

    mv_image_data_dir=$(docker inspect pmmdata | egrep "Source" | sed 's/ "Source": "//' | sed 's/_data",/_data\/* \/mnt\/disks\/pmmdata/')

    image_data_dir=$(docker inspect pmmdata | egrep "Source" | sed 's/ "Source": "//' | sed 's/_data",/_data/')
    
    echo "mv " $mv_image_data_dir
    
    echo "rmdir " $image_data_dir
    
    echo "ln -s /mnt/disks/pmmdata " $image_data_dir
     
    deploy_pmm_server=$(docker run -itd -p 7443:443 --volumes-from pmmdata --name pmm-server  -v /etc/pmm-certs:/srv/nginx --restart always xyz/percona/pmm-server-updated:2.34.0)    

else

    echo "image is corrupted or pmmdata image already exists"
    
fi
