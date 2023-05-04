#!/bin/env python

#ToDo
#create pmm user on db


import argparse
import subprocess
import shlex
import logging
import socket
import shutil

def process_args():                # to pass args
    parser = argparse.ArgumentParser(description=' usage: " xyz "  ', epilog='Default Log Destination - /tmp')
    parser.add_argument("-data_center", "--data_center", help="primary dc ", type=str, required=True)
    args = parser.parse_args()
    return args
args = process_args()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


host_info=socket.getfqdn().split('.',1)[0] #hostname
mysql_socket_mycnf=" cat /etc/my.cnf | grep '.sock'| head -1 | awk -F '=' '{print $2}' "
mysql_socket_cmd=subprocess.Popen(mysql_socket_mycnf, shell=True,stdout=subprocess.PIPE)
mysql_socket_value=(mysql_socket_cmd.communicate()[0]).strip()
pmm_client_env=(socket.getfqdn().split('.',2)[1])
pmm_client_dc=(socket.getfqdn().split('.',3)[2])


if  pmm_client_env == "test":
  pmm_server="test.pmmserver.com"
  server_url="https://admin:admin@test.pmmserver.com:7443"
elif pmm_client_env  == "production":
  pmm_server="prod.pmmserver.com"
  server_url="https://admin:admin@prod.pmmserver.com:7443"



check_pmm=" pmm-admin status | grep  'mysql' | wc -l "
check_pmm_cmd=subprocess.Popen(check_pmm, shell=True,stdout=subprocess.PIPE)
check_pmm_status=int(check_pmm_cmd.communicate()[0])
pmmuser=PMM_USER
pmmpassword=PMM_PASSWD
dbuser=METRICS_USER
dbpassword=METRICS_PASSWD



def setup_pmmclient():
    cmd = "mysql -NBe 'select variable_value from performance_schema.global_variables where variable_name=read_only;'"

    read_oly=subprocess.Popen([cmd], shell=True,stdout=subprocess.PIPE)

    read_only=read_oly.communicate()[0].strip()

    if read_only not in ['ON','OFF']:

       logging.info("Please check if mysql is running")

    else:

         read_only == "OFF" and check_pmm_status == 0 and pmm_client_dc == args.data_center:

         install_pmmclient = " yum install -y pmmclient-2.34"

         install_pmmclient_cmd=subprocess.Popen(install_pmmclient, shell=True,stdout=subprocess.PIPE)

         install_pmmclient_exec=(install_pmmclient_cmd.communicate()[0])

         setup_pmmclient_node_metrics = ("pmm-admin config  --server-url=" + server_url + ">&/tmp/pmmclient")

         setup_pmmclient_mysql_metrics = ("pmm-admin add mysql  --environment=" + pmm_client_group + " --username=" + pmmuser + " --socket=" + mysql_socket_value + " --password=" +"'"+ str(pmmpassword) +"'" + " --query-source=perfschema "  + host_info)

         setup_pmmclient_node_metrics_cmd=subprocess.Popen(setup_pmmclient_node_metrics, shell=True,stdout=subprocess.PIPE)

         setup_pmmclient_exec=(setup_pmmclient_node_metrics_cmd.communicate()[0])

         setup_pmmclient_mysql_metrics_cmd=subprocess.Popen(setup_pmmclient_mysql_metrics, shell=True,stdout=subprocess.PIPE)

         setup_pmmclient_exec=(setup_pmmclient_mysql_metrics_cmd.communicate()[0])

         shutil.copy2('/xyz/custom-metrics/connections-count.yml', '/usr/local/percona/pmm2/collectors/custom-queries/mysql/low-resolution')         
         
         restart_pmm_agent_cmd = "service pmm-agent restart"

         logging.info("restarting pmm-agent")

         restart_pmm_agent=subprocess.check_output(shlex.split(restart_pmm_agent_cmd))

       elif read_only == "ON" and pmm_client_dc != args.data_center:

         uninstall_pmmclient = "yum remove -y  pmmclient-2.34"

         uninstall_pmmclient_cmd =subprocess.check_output(shlex.split(uninstall_pmmclient)).strip()

         uninstall_pmmclient_cmd=subprocess.Popen(uninstall_pmmclient, shell=True,stdout=subprocess.PIPE)

         uninstall_pmmclient_exec=(uninstall_pmmclient_cmd.communicate()[0])

         logging.info("pmm_client is uninstalled on replica")

       else:

          logging.info("unable to setup pmmclient, please check data center and read_only setting")

def main():

  setup_pmmclient()

if __name__ == '__main__':

  main()
