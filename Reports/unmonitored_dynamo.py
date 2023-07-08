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
#profile=["klickpay"]


dynamo123=""
for p in profile:
        for re in region:
                CMD="aws dynamodb list-tables --profile "+ p + " --region "+ re +" | tr '\n' ' ' "
                print(p,"->",re)
                output=subprocess.check_output(CMD,shell=True)
                dynamo23=output.decode('ASCII').replace(" ", "").replace("[","").replace("]","").replace('"',"").replace("{TableNames:","").replace("}","") #.strip()) #.split(',')
                dynamo123=dynamo123+","+dynamo23
dynamo_aws=dynamo123.replace(',', '', 1).split(',')
#print(dynamo_aws)

r = requests.post(ZABBIX_API_URL,
        json={
        "jsonrpc": "2.0",
        "method": "application.get",
                "params": {
                "output": ["name"],
                "groupids": "301",

                },
        "id": 2,
        "auth": AUTHTOKEN
        })

#print(json.dumps(r.json(), indent=4, sort_keys=True))
dynamo_zabbix=[]
for item in r.json()["result"]:
        if "dynamodbname" in item['name'].lower():
                dynamo_zabbix.append(item['name'].split(':')[1].strip())
#print(dynamo_zabbix)

#result_1 = list(set(print(dynamo_zabbix)).difference(dynamo_aws))
result_1=[item for item in dynamo_aws if item not in dynamo_zabbix]
#print(result_1)
#print()

if result_1==[] or result_1==[''] :
        string="\nYIPPEE! ALL DYNAMODBs ARE GETTING MONITORED."
else:
        string = "\n".join(result_1)
#print(string)

r = requests.post(ZABBIX_API_URL,
json={
"jsonrpc": "2.0",
"method": "user.logout",
"params": {},
"id": 2,
"auth": AUTHTOKEN
})

SENDMAIL="""echo "Hello team,\nThis report is published for Unmonitored DynamoDBs in Zabbix.\n\n%s\n\nRegards,\nabc team" | mailx -r "abc@example.com" -s "Unmonitored DynamoDB Zabbix" abc@example.com""" %(string)


print(SENDMAIL)

SENDMAIL=str(SENDMAIL)
send=subprocess.call(SENDMAIL,shell=True)
