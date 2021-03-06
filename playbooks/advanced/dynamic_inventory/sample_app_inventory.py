#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Dynamic Inventory that can collect inventory abount web,app,dbs servers
#
import os
import re
import sys
import ConfigParser

from novaclient import client as nova_client

try:
    import json
except:
    import simplejson as json


FILENAME = 'sample_app_inventory.ini'
STACK_SECTION = 'stack'
APP_SECTION = 'sample_app'
CONFIG_FILES = ['%s/%s' % (os.path.dirname(sys.argv[0]), FILENAME),
                os.path.expanduser(
                    os.environ.get('ANSIBLE_CONFIG', '~/' + FILENAME)),
                "/etc/ansible/" + FILENAME]

TARGET_LIST = ['lbs', 'web', 'app', 'dbs']

config = ConfigParser.SafeConfigParser()


def get_nova_client():
    # create novaclient that is described information in stack_inventory.ini
    # result = nova.client.Client(...)
    version = config.get(STACK_SECTION, 'api_version')
    username = config.get(STACK_SECTION, 'os_username')
    password = config.get(STACK_SECTION, 'os_password')
    auth_url = config.get(STACK_SECTION, 'os_auth_url')
    region_name = config.get(STACK_SECTION, 'os_region_name')
    tenant_name = config.get(STACK_SECTION, 'os_tenant_name')

    instance = nova_client.Client(version,
                                  username,
                                  password,
                                  tenant_name,
                                  auth_url,
                                  region_name=region_name)
    return instance


def name_filter(servers):
    # create list of server instance that is filtered by hostname
    # result = { TARGET: [Server-A, Server-B, ...] }
    result = {}
    for target in TARGET_LIST:
        node_list = []
        pattern = '^%s' % config.get(APP_SECTION,
                                     '%s_hostname_prefix' % target)
        for server in servers:
            if re.match(pattern, server.name):
                node_list.append(server)
        if len(node_list) > 0:
            result[target] = node_list
    return result


def do_list(target_list):
    # get a inventory for all hosts
    return _create_inventory(target_list)


def do_host(target_list, host):
    # get a inventory for particular host
    # it is same information as hostvars in _meta section
    groups = _create_inventory(target_list)
    if host in groups['_meta']['hostvars']:
        return groups['_meta']['hostvars'][host]
    return {}


def usage():
    print('Usage: stack_inventory --list')
    print('       stack_inventory --host <hostname|IPAddress>')
    sys.exit(1)


def _create_inventory(target_list):
    groups = {
        'localhost': {
            'hosts': ['localhost'],
            'vars': {
                'ansible_connection': 'local'
            }
        }
    }
    meta = dict(hostvars=dict())
    web_addr = []
    app_addr = []
    dbs_addr = []

    # create group entory to inventory data
    for key in target_list.keys():
        groups[key] = dict(hosts=list(), vars=dict())
        for server in target_list[key]:
            info = server.addresses
            groups[key]['hosts'].append(info['dmz-net'][0]['addr'])
            if key == 'web':
                web_addr.append(info['dmz-net'][0]['addr'])
            if key == 'app':
                app_addr.append(info['app-net'][0]['addr'])
            if key == 'dbs':
                dbs_addr.append(info['dbs-net'][0]['addr'])
    if 'lbs' in groups and 'web' in groups:
        if len(web_addr) > 0:
            groups['lbs']['vars'] = dict(webs=web_addr)
    if 'web' in groups and 'app' in groups:
        if len(app_addr) > 0:
            groups['web']['vars'] = dict(app=app_addr[0])
    if 'app' in groups and 'dbs' in groups:
        if len(dbs_addr) > 0:
            groups['app']['vars'] = dict(dbs=dbs_addr[0])

    # create _meta section for each host
    for key in target_list.keys():
        for host in groups[key]['hosts']:
            if groups[key]['vars']:
                 meta['hostvars'][host] = groups[key]['vars']
            else:
                 meta['hostvars'][host] = {}
    groups['_meta'] = meta
    return groups


def main(host=None):
    nova = get_nova_client()
    target_list = name_filter(nova.servers.list())
    if host is None:
        print(json.dumps(do_list(target_list), sort_keys=True, indent=2))
    else:
        print(json.dumps(do_host(target_list, host), sort_keys=True, indent=2))


if __name__ == '__main__':
    for path in CONFIG_FILES:
        if os.path.exists(path):
            config.read(path)
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        main()
    elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        main(sys.argv[2])
    else:
        usage()


#
# [EOF]
#
