import requests
import json
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

profile=["accountName"]
region=["ap-south-1"]


rds123=""
for p in profile:
        for re in region:
                CMD="aws elb describe-load-balancers --query \"LoadBalancerDescriptions[*].LoadBalancerName\" --profile "+ p + " --region "+ re +" | tr '\n' ' ' "
                print(p,"->",re)
                output=subprocess.check_output(CMD,shell=True)
                rds23=output.decode('ASCII').replace(" ", "").replace("[","").replace("]","").replace('"',"") #.strip()) #.split(',')
                rds123=rds123+","+rds23
rds_aws=rds123.replace(',', '', 1).split(',')
#print(rds_aws)

r = requests.post(ZABBIX_API_URL,
        json={
        "jsonrpc": "2.0",
        "method": "application.get",
                "params": {
                "output": ["name"],
                "groupids": "111",
                
                },
        "id": 2,
        "auth": AUTHTOKEN
        })

#print(json.dumps(r.json(), indent=4, sort_keys=True))
rds_zabbix=[]
for item in r.json()["result"]:
        if "elbname" in item['name'].lower():
                rds_zabbix.append(item['name'].split(':')[1].strip())
#print(rds_zabbix)

#result_1 = list(set(print(rds_zabbix)).difference(rds_aws))
result_1=[item for item in rds_aws if item not in rds_zabbix]
#print(result_1)
#print()
#string = "\n".join(result_1) 
#print(string)

if result_1==[] or result_1==[''] :
        string="\nYIPPEE! ALL ELBs ARE GETTING MONITORED."
else:
        string = "\n".join(result_1)

r = requests.post(ZABBIX_API_URL,
json={
"jsonrpc": "2.0",
"method": "user.logout",
"params": {},
"id": 2,
"auth": AUTHTOKEN
})

SENDMAIL="""echo "Hello team,\
This report is published for Unmonitored ELB in Zabbix.\

%s

Regards,\

abc team" | mailx -r "abc@example.com" -s "Unmonitored ELB Zabbix" abc@example.com""" %(string)

#print(SENDMAIL)

SENDMAIL=str(SENDMAIL)
send=subprocess.call(SENDMAIL,shell=True)
