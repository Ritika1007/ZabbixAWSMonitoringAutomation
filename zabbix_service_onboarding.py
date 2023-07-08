import requests
import json
import configparser
from optparse import OptionParser
from cryptography.fernet import Fernet
import sys
import string
import random
import glob, os

#jenkins workspace where scripts will be kept
WORKSPACE=str(sys.argv[1])
WORKSPACE=WORKSPACE+"/zabbix-automation"

#service name with which host will be created on zabbix
#input from jenkins job
AWS_ACCOUNT=str(sys.argv[2])
SERVICE_NAME=str(sys.argv[3])

#print(AWS_ACCOUNT, SERVICE_NAME, WORKSPACE)

#list of all macros passed to zabbix
config_list=[]

#reading AWS cloud-watch creds
filename=WORKSPACE+"/conf/AWSCreds.conf"
config = configparser.ConfigParser()
config.read(filename)

KEY = config[AWS_ACCOUNT]['AWS_ACCESS_KEY_ID']
SECRET = config[AWS_ACCOUNT]['AWS_ACCESS_SECRET']

config_dict1 = {
                                "macro": "{$AWS_ACCESS_KEY_ID}",
                                "value": KEY
                            }
config_dict2 ={
                                "macro": "{$AWS_ACCESS_SECRET}",
                                "value": SECRET,
                                "type": 1
                            }
config_list.append(config_dict1)
config_list.append(config_dict2)


#reading threshold.conf file
dir_conf=WORKSPACE+"/services/"+SERVICE_NAME.strip()
os.chdir(dir_conf)
If_rds=0
for file in glob.glob("*.conf"):
    parser = configparser.ConfigParser(delimiters=('='))
    parser.optionxform = str
    parser.read(file)

    if "rds" in file:
        If_rds=1
        rds_dl_dict={}
        for sect in parser.sections():
            for name, value in parser.items(sect):
                if "teamdl" in name.lower():
                        if "_" in name:
                            nm=name.split('_')[1]
                            rds_DL= value.split(',')
                            rds_DL.append('abc@example.com')
                            rds_dl_dict[nm] = rds_DL
                            print(rds_dl_dict)
                        else:
                            rds_DL_2= value.split(',')
                            rds_DL_2.append('abc@example.com')
                            print (rds_DL_2)
                else:
                    config_dict = {}
                    config_dict["macro"]=name
                    config_dict["value"]=value
                    config_list.append(config_dict)
                    if "rds_names" in name.lower():
                        rds=value.split('|')
    elif "teamdl" in file:
        DL=str(parser['action']['teamDL']).split(',')
        DL.append('abc@example.com')

    else:
        for sect in parser.sections():
            for name, value in parser.items(sect):
                config_dict = {}
                config_dict["macro"]=name
                config_dict["value"]=value
                config_list.append(config_dict)

#print(config_list)

filename=WORKSPACE+"/conf/zab.txt"

with open(filename, 'rb') as mykey:
        key = mykey.read()

f = Fernet(key)

ZABBIX_API_URL = "https://monitor.example.in/zabbix/api_jsonrpc.php"

filename=WORKSPACE+"/conf/enc.conf"
with open(filename, 'rb') as encrypted_file:
    encrypted = encrypted_file.read()

decrypted = f.decrypt(encrypted).decode('UTF-8')
UNAME,PWORD=decrypted.split(':')


#retrieving access token
r = requests.post(ZABBIX_API_URL,
                  json={
                      "jsonrpc": "2.0",
                      "method": "user.login",
                      "params": {
                          "user": UNAME.strip(),
                          "password": PWORD.strip()},
                      "id": 1
                  })

#print(json.dumps(r.json(), indent=4, sort_keys=True))
if r.json()["result"] != []:
    AUTHTOKEN = r.json()["result"]
else:
    print("\033[1;31mAuthentication Failed\033[0;0m")
    exit()

#checking if host already exists
r = requests.post(ZABBIX_API_URL,
                  json={
                      "jsonrpc": "2.0",
                       "method": "host.get",
                        "params": {
                            "output": ["hostid"],
                            "filter": {
                                "host": [
                                    SERVICE_NAME
                                ]
                            }
                        },

                      "id": 2,
                      "auth": AUTHTOKEN
                  }

)

#if not create host in zabbix with service name passed
if r.json()["result"] == []:

    #retrieving template id of Parent Template AWS Services
    r = requests.post(ZABBIX_API_URL,
                    json={
                        "jsonrpc": "2.0",
                        "method": "template.get",
                            "params": {
                                "output": ["templateid"],
                                "filter": {
                                    "host": [
                                        "Parent Template AWS Services"
                                    ]
                                }
                            },

                        "id": 2,
                        "auth": AUTHTOKEN
                    }

    )
    for item in r.json()["result"]:
        TEMPLATEID = item["templateid"]

    #check if host group already exists with the service name
    r = requests.post(ZABBIX_API_URL,
                    json={
                        "jsonrpc": "2.0",
                        "method": "hostgroup.get",
                            "params": {
                                "output": "extend",
                                "filter": {
                                    "name": [
                                        SERVICE_NAME
                                    ]
                                }
                            },

                        "id": 2,
                        "auth": AUTHTOKEN
                    })
    if r.json()["result"] != []:
        for item in r.json()["result"]:
            if "groupid" in item:
                GROUPID = item["groupid"]

    #if host-group not present create it
    else:
        r1 = requests.post(ZABBIX_API_URL,
                    json={
                        "jsonrpc": "2.0",
                        "method": "hostgroup.create",
                        "params": {
                            "name": SERVICE_NAME
                        },

                        "id": 2,
                        "auth": AUTHTOKEN
                    })
        #print(json.dumps(r1.json()["result"]["groupids"], indent=4, sort_keys=True))
        for item in r1.json()["result"]["groupids"]:
            GROUPID = item

    #creating host
    r = requests.post(ZABBIX_API_URL,
                    json={
                        "jsonrpc": "2.0",
                        "method": "host.create",
                        "params": {
                            "host": SERVICE_NAME,
                            "interfaces": [
                                {
                                    "type": 1,
                                    "main": 1,
                                    "useip": 1,
                                    "ip": "127.0.0.1",
                                    "dns": "",
                                    "port": "10050"
                                }
                            ],
                            "groups": [
                                {
                                    "groupid": GROUPID
                                },
                                {
                                    "groupid": 111
                                }
                            ],
                            "templates": [
                                {
                                    "templateid": TEMPLATEID
                                }
                            ],
                            "macros": config_list

                        },

                        "id": 2,
                        "auth": AUTHTOKEN
                    })

    print(json.dumps(r.json(), indent=4, sort_keys=True))

    if r.json()["result"] != []:
        for item in r.json()["result"]["hostids"]:
            HOSTID = item
            print("\033[1;32mHost Created Succesfully in Zabbix with ID:",HOSTID,"\033[0;0m")
        N = 9
        res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=N))

        #creating user to which notification will be sent
        r = requests.post(ZABBIX_API_URL,
                  json={
                "jsonrpc": "2.0",
                "method": "user.create",
                "params": {
                    "alias": SERVICE_NAME.lower(),
                    "passwd": str(res),
                    "type": 3,
                    "usrgrps": [
                        {
                            "usrgrpid": "7"
                        }
                    ],
                    "user_medias": [
                        {
                            "mediatypeid": "6",
                            "sendto": DL,
                            "active": 0,
                            "severity": 63,
                            "period": "1-7,00:00-24:00"
                        }
                    ]
                },
                "id": 2,
                "auth": AUTHTOKEN
        })
        print(json.dumps(r.json(), indent=4, sort_keys=True))
        if r.json()["result"] != []:
            for item in r.json()["result"]["userids"]:
                USERID = item
            # if user created successfully create action
            r = requests.post(ZABBIX_API_URL,
                  json={
                "jsonrpc": "2.0",
                "method": "action.create",
                "params": {
                    "name": SERVICE_NAME,
                    "eventsource": 0,
                    "status": 0,
                    "esc_period": "1h",
                    "filter": {
                        "evaltype": 0,
                        "conditions": [
                            {
                                "conditiontype": 1,
                                "operator": 0,
                                "value": HOSTID
                            },
                            {
                                "conditiontype": 25,
                                "operator": 1,
                                "value": "RDSName"
                            }
                        ]
                    },
                    "operations": [
                        {
                            "operationtype": 0,
                            "esc_period": "0s",
                            "esc_step_from": 1,
                            "esc_step_to": 1,
                            "evaltype": 0,
                            "opmessage_usr": [
                                {
                                    "userid": USERID
                                }
                            ],
                            "opmessage": {
                                "default_msg": 0,
                                "subject": "Problem: {EVENT.NAME}",
                                "message": """Problem started at {EVENT.TIME} on {EVENT.DATE}
Problem name: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
{TRIGGER.DESCRIPTION}
Original problem ID: {EVENT.ID}
{TRIGGER.URL}""",
                                "mediatypeid": "6"
                            }
                        }
                    ],
                "recovery_operations":[
                    {
                        "operationtype": "0",
                        "opmessage_usr": [
                                {
                                    "userid": USERID
                                }
                            ],
                        "opmessage": {
                        "default_msg": 0,
                        "subject": "Resolved: {EVENT.NAME}",
                        "message": """Problem resolved at {EVENT.RECOVERY.TIME} on {EVENT.RECOVERY.DATE}
Problem name: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
{TRIGGER.DESCRIPTION}
Original problem ID: {EVENT.ID}
{TRIGGER.URL}""",
                    "mediatypeid": "6"
                            }
                    }
                ]
                },
                "id": 2,
                "auth": AUTHTOKEN
})
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        #rds
        if If_rds==1:
            for r1 in rds:
              if r1 in rds_dl_dict.keys():
                DL_rds=rds_dl_dict[r1]
              else:
                if "default" in rds_dl_dict.keys():
                    DL_rds=rds_dl_dict['default']
                else: 
                    DL_rds=rds_DL_2
                
                r = requests.post(ZABBIX_API_URL,
                    json={
                    "jsonrpc": "2.0",
                    "method": "user.create",
                    "params": {
                        "alias": r1.lower(),
                        "passwd": str(res),
                        "type": 3,
                        "usrgrps": [
                            {
                                "usrgrpid": "7"
                            }
                        ],
                        "user_medias": [
                            {
                                "mediatypeid": "6",
                                "sendto": DL_rds,
                                "active": 0,
                                "severity": 63,
                                "period": "1-7,00:00-24:00"
                            }
                        ]
                    },
                    "id": 2,
                    "auth": AUTHTOKEN
            })
                print(json.dumps(r.json(), indent=4, sort_keys=True))
                if r.json()["result"] != []:
                    for item in r.json()["result"]["userids"]:
                        USERID = item
                # if user created successfully create action
                    r = requests.post(ZABBIX_API_URL,
                        json={
                    "jsonrpc": "2.0",
                    "method": "action.create",
                    "params": {
                        "name": "RDS-"+r1+"-Action",
                        "eventsource": 0,
                        "status": 0,
                        "esc_period": "1h",
                        "filter": {
                            "evaltype": 0,
                            "conditions": [
                                {
                                    "conditiontype": 26,
                                    "operator": 0,
                                    "value2": "RDSName",
                                    "value" : r1
                                }
                            ]
                        },
                        "operations": [
                            {
                                "operationtype": 0,
                                "esc_period": "0s",
                                "esc_step_from": 1,
                                "esc_step_to": 1,
                                "evaltype": 0,
                                "opmessage_usr": [
                                    {
                                        "userid": USERID
                                    }
                                ],
                                "opmessage": {
                                    "default_msg": 0,
                                    "subject": "Problem: {EVENT.NAME}",
                                    "message": """Problem started at {EVENT.TIME} on {EVENT.DATE}
Problem name: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
{TRIGGER.DESCRIPTION}
Original problem ID: {EVENT.ID}
{TRIGGER.URL}""",
                                    "mediatypeid": "6"
                                }
                            }
                        ],
                        "recovery_operations":[
                        {
                            "operationtype": "0",
                            "opmessage_usr": [
                                    {
                                        "userid": USERID
                                    }
                                ],
                            "opmessage": {
                            "default_msg": 0,
                            "subject": "Resolved: {EVENT.NAME}",
                            "message": """Problem resolved at {EVENT.RECOVERY.TIME} on {EVENT.RECOVERY.DATE}
Problem name: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
{TRIGGER.DESCRIPTION}
Original problem ID: {EVENT.ID}
{TRIGGER.URL}""",
                        "mediatypeid": "6"
                            }
                    }
                ]
                    },
                    "id": 2,
                    "auth": AUTHTOKEN
    })
                    print(json.dumps(r.json(), indent=4, sort_keys=True))




    else:
        print(json.dumps(r.json(), indent=4, sort_keys=True))




#if host already exists update macros
else:
    for item in r.json()["result"]:
        HOSTID=item["hostid"]
    #Updating Host Macros
    r = requests.post(ZABBIX_API_URL,
                    json={
                        "jsonrpc": "2.0",
                        "method": "host.update",
                        "params": {
                            "hostid": HOSTID,
                            "macros": config_list
                        },

                    "id": 2,
                    "auth": AUTHTOKEN

                    })
    print(json.dumps(r.json(), indent=4, sort_keys=True))
    if If_rds == 1:
         for r1 in rds:
            r = requests.post(ZABBIX_API_URL,
                  json={
                    "jsonrpc": "2.0",
                    "method": "action.get",
                    "params": {
                        "selectFilter": "extend",
                        "filter": {
                            "name": "RDS-"+r1+"-Action"
                        }
                    },
                    "id": 2,
                    "auth": AUTHTOKEN
                  })
            if r.json()["result"] == []:
                N = 9
                res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=N))
                if r1 in rds_dl_dict.keys():
                    DL_rds=rds_dl_dict[r1]
                else:
                    if "default" in rds_dl_dict.keys():
                        DL_rds=rds_dl_dict['default']
                    else: 
                        DL_rds=rds_DL_2
                r = requests.post(ZABBIX_API_URL,
                    json={
                    "jsonrpc": "2.0",
                    "method": "user.create",
                    "params": {
                        "alias": r1.lower(),
                        "passwd": str(res),
                        "type": 3,
                        "usrgrps": [
                            {
                                "usrgrpid": "7"
                            }
                        ],
                        "user_medias": [
                            {
                                "mediatypeid": "6",
                                "sendto": DL_rds,
                                "active": 0,
                                "severity": 63,
                                "period": "1-7,00:00-24:00"
                            }
                        ]
                    },
                    "id": 2,
                    "auth": AUTHTOKEN
            })
                print(json.dumps(r.json(), indent=4, sort_keys=True))
                if r.json()["result"] != []:
                    for item in r.json()["result"]["userids"]:
                        USERID = item
                    r = requests.post(ZABBIX_API_URL,
                        json={
                    "jsonrpc": "2.0",
                    "method": "action.create",
                    "params": {
                        "name": "RDS-"+r1+"-Action",
                        "eventsource": 0,
                        "status": 0,
                        "esc_period": "1h",
                        "filter": {
                            "evaltype": 0,
                            "conditions": [
                                {
                                    "conditiontype": 26,
                                    "operator": 0,
                                    "value2": "RDSName",
                                    "value" : r1
                                }
                            ]
                        },
                        "operations": [
                            {
                                "operationtype": 0,
                                "esc_period": "0s",
                                "esc_step_from": 1,
                                "esc_step_to": 1,
                                "evaltype": 0,
                                "opmessage_usr": [
                                    {
                                        "userid": USERID
                                    }
                                ],
                                "opmessage": {
                                    "default_msg": 0,
                                    "subject": "Problem: {EVENT.NAME}",
                                    "message": """Problem started at {EVENT.TIME} on {EVENT.DATE}
Problem name: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
{TRIGGER.DESCRIPTION}
Original problem ID: {EVENT.ID}
{TRIGGER.URL}""",
                                    "mediatypeid": "6"
                                }
                            }
                        ],
                        "recovery_operations":[
                        {
                            "operationtype": "0",
                            "opmessage_usr": [
                                    {
                                        "userid": USERID
                                    }
                                ],
                            "opmessage": {
                            "default_msg": 0,
                            "subject": "Resolved: {EVENT.NAME}",
                            "message": """Problem resolved at {EVENT.RECOVERY.TIME} on {EVENT.RECOVERY.DATE}
Problem name: {EVENT.NAME}
Severity: {EVENT.SEVERITY}
{TRIGGER.DESCRIPTION}
Original problem ID: {EVENT.ID}
{TRIGGER.URL}""",
                        "mediatypeid": "6"
                            }
                    }
                ]
                    },
                    "id": 2,
                    "auth": AUTHTOKEN
    })
                    print(json.dumps(r.json(), indent=4, sort_keys=True))


#logout user
r = requests.post(ZABBIX_API_URL,
                  json={
                      "jsonrpc": "2.0",
                      "method": "user.logout",
                      "params": {},
                      "id": 2,
                      "auth": AUTHTOKEN
                      })
