import requests
#import json
import subprocess
from cryptography.fernet import Fernet




with open('zab.txt', 'rb') as mykey:
        key = mykey.read()

f = Fernet(key)

with open('enc.conf', 'rb') as encrypted_file:
    encrypted = encrypted_file.read()

decrypted = f.decrypt(encrypted).decode('UTF-8')
UNAME,PWORD=decrypted.split(':')

ZABBIX_API_URL = "https://monitor.example.in/zabbix/api_jsonrpc.php"


logfile = open("zabbix_aws.csv","w")
logfile.write("IP" + "," + "InstanceName" + "," + "ZabbixHostName" + "," + "Zabbix_Status"+ "\n")

r = requests.post(ZABBIX_API_URL,
                  json={
                      "jsonrpc": "2.0",
                      "method": "user.login",
                      "params": {
                          "user": UNAME,
                          "password": PWORD},
                      "id": 1
                  })
AUTHTOKEN = r.json()["result"]

profile=['accountName']
region=["ap-south-1"] #,"ap-southeast-1","us-east-1","us-west-2"]

count=0

for p in profile:
        for re in region:
                CMD="aws ec2 describe-instances --filters Name=instance-state-name,Values=running --query 'Reservations[*].Instances[*].[PrivateIpAddress]' --output text --profile "+ p + " --region "+ re +" | tr '\n' ',' "
                print(p,"->",re)
                output=subprocess.check_output(CMD,shell=True)
                host23=output.decode('ASCII').split(',')
                host23.pop()
                for h in host23:
                        r = requests.post(ZABBIX_API_URL,
                                        json={
                                        "jsonrpc": "2.0",
                                        "method": "host.get",
                                                "params": {
                                                "output": ["host", "status"],
                                                "search": {
                                                        "ip": h
                                                        },
                                                        "searchWildcardsEnabled": True,
                                                        "searchByAny": True,
                                                },
                                                
                                                                        
                                        "id": 2,
                                        "auth": AUTHTOKEN
                                        })
                        if r.json()["result"] != []:
                                for item in r.json()["result"]:
                                        HostName = item["host"]
                                        Status = item["status"]
                                        cmd="aws ec2 describe-instances --filters Name=private-ip-address,Values="+h+" --profile "+ p + " --region "+ re +" --query 'Reservations[].Instances[].Tags[?Key == `Name`].Value'"
                                        output=subprocess.check_output(cmd,shell=True)
                                        if "example" in output.decode('ASCII') or "eks" in output.decode('ASCII'):
                                                        pass
                                        else:
                                                if int(Status) == 0:
                                                        #logfile.write(h+ ","+ output.decode('ASCII').split('"')[1] +","+ HostName+ ",Enabled" + "\n")
                                                        #logfile.write(h+ ","+ str(output) +","+ HostName+ ",Enabled" + "\n")
                                                        pass
                                                if int(Status) == 1:
                                                # cmd="aws ec2 describe-instances --filters Name=private-ip-address,Values="+h+" --profile "+ p + " --region "+ re +" --query 'Reservations[].Instances[].Tags[?Key == `Name`].Value'"
                                                #output=subprocess.check_output(cmd,shell=True)
                                                #if "example" in output.decode('ASCII') or "eks" in output.decode('ASCII'):
                                                        #pass
                                                #else:     
                                                        #logfile.write(h+ ","+ output.decode('ASCII').split('"')[1] +","+ HostName+ ",Disabled" + "\n")
                                                        #print(h," : ",output.decode('ASCII')," : ","Disabled")
                                                        logfile.write(h+ ","+ str(output) +","+ HostName+ ",Disabled" + "\n")
                        else:
                                cmd="aws ec2 describe-instances --filters Name=private-ip-address,Values="+h+" --profile "+ p + " --region "+ re +" --query 'Reservations[].Instances[].Tags[?Key == `Name`].Value'"
                                output=subprocess.check_output(cmd,shell=True)
                                
                                if "example" in output.decode('ASCII') or "eks" in output.decode('ASCII'):
                                                        pass
                                else:
                                        #print(h," : ",output.decode('ASCII')," : ","Does Not Exist")
                                        """
                                        if output.decode('ASCII') == '[]':
                                                logfile.write(h+ ", NA ,"+ HostName+ ",Does Not Exist" + "\n")
#                                                print(h," : ",output.decode('ASCII')," : ","Does Not Exist")
                                        else:
                                                logfile.write(h+ ","+ output.decode('ASCII').split('"')[1] +",NA,Does Not Exist" + "\n")"""
                                        logfile.write(h+ ","+ str(output) +",NA,Does Not Exist" + "\n")
                                        


r = requests.post(ZABBIX_API_URL,
                  json={
                      "jsonrpc": "2.0",
                      "method": "user.logout",
                      "params": {},
                      "id": 2,
                      "auth": AUTHTOKEN
                  })
