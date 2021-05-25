#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import requests

# args = sys.argv
# conf_file = args[1]
conf_file = "./login.json"

def get_all_vm_inventory():
  with open(conf_file, "r") as file:
    conf = file.read()
    conf = json.loads(conf)
  prism_addr = conf["prism_address"]
  prism_user = conf["user_name"]
  prism_pass = conf["password"]

  base_url = 'https://' + prism_addr + ':9440/PrismGateway/services/rest/v2.0/'
  insecure_warn = requests.packages.urllib3.exceptions.InsecureRequestWarning
  requests.packages.urllib3.disable_warnings(insecure_warn)
  s = requests.Session()
  s.auth = (prism_user, prism_pass)
  s.headers.update({'Content-Type': 'application/json; charset=utf-8'})

  # Get VM.
  url = base_url + 'vms/?include_vm_nic_config=true'
  vms = s.get(url, verify=False).json()

  inventory = {
    "all":{"hosts": []},
    "_meta": {
      "hostvars": {}
    }
  }
  vm_entities = []
  hosts = {}
  for vm in vms['entities']:
    #print(json.dumps(vm, indent=2))
    vm_name = vm['name']
    power_state = vm['power_state']
    inventory["all"]["hosts"].append(vm_name)
    if(vm['vm_nics']):
      vm_nic = vm['vm_nics'][0]
      ip_address = vm_nic.get('ip_address')
      requested_ip_address = vm_nic.get('requested_ip_address')
      if (ip_address == None):
        ip_address = vm_nic.get('requested_ip_address')
      if ip_address:
        inventory["_meta"]["hostvars"][vm_name] = {"ansible_host": ip_address}
      else:
        inventory["_meta"]["hostvars"][vm_name] = {}
  return(inventory)

if __name__ == '__main__':
  hostname = None
  inventory = get_all_vm_inventory()

  if len(sys.argv) > 1:
    if sys.argv[1] == "--host":
      hostname = sys.argv[2]

  if hostname:
    if inventory["_meta"]["hostvars"][hostname]:
      print(json.dumps(inventory["_meta"]["hostvars"][hostname]))
  else:
    print(json.dumps(inventory))
