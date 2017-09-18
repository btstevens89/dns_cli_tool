#! /usr/bin/env python

## TODO: Exception Handling
## 

# Have user input MAC or IP Address

import certifi
import fnmatch
import getpass
import json
import ipaddress   # This is for IP address validation
import logging
import os
import re
import requests
import sys
import time
import urllib3
import validators
from infoblox_client import connector
from infoblox_client import objects
from ipInfo import *

mac_data_dir = 'path/to/dir'
dupe = 'path/to/dir'
filepath = 'path/to/dir'

# These are for the infoblox lab test environment
infoblox_IP = 'xx.xx.xx.xx'   # needs to be IP of prod infoblox appliance
infoblox_username = 'username'     
infoblox_password = 'password'    
infoblox_zone = '.some.domain.com' 
opts = {'host': infoblox_IP, 'username': infoblox_username, 'password': infoblox_password}
conn = connector.Connector(opts)
wapi_url = 'https://infoblox-test-environment.com/wapi/v2.2.2/'

#################################################################################
############################    Infoblox Functions    ###########################
#################################################################################

def infobloxAuto():
    os.system('cls')
    print('Please choose from the following list of options:')
    print('1. Manage A Record(s)')
    print('2. Manage CNAME Record(s)')
    print('3. Manage TXT Record(s)')
    print('4. Return to Main Menu')
    print('5. Exit')
    while True:
        try:
            infoblox_choice = int(input('> '))
            if int(infoblox_choice) == 1:
                aRecord()
            elif int(infoblox_choice) == 2:
                cnameRecord()
            elif int(infoblox_choice) == 3:
                txtRecord()
            elif int(infoblox_choice) == 4:
                mainMenu()
            elif int(infoblox_choice) == 5:
                sys.exit('Exiting the program!')
            else:
                print('\nInvalid selection!\n\n')
                continue
        except ValueError:
            print('\nInvalid selection!')
            continue

def aRecord():
    x = 0
    a_record_ips = []
    a_record_names = []
    os.system('cls')
    print('[A Record] Please make a selection:')
    print('1. Record Addition')
    print('2. Record Removal')
    print('3. Return to Infoblox Menu')
    user_choice = input('> ')
    if int(user_choice) == 1:
        print('''
            ***************************************************************************************
            **** NOTE: After entering the final record addition, just press [ENTER] to proceed ****
            ***************************************************************************************
            ''')
        while True:
            print('What is the IP address of the A record?')
            record_IP = input('> ')
            if record_IP == '':
                if len(a_record_ips) < 1:
                    print('\nReturning to Main Menu!\n')
                    time.sleep(3)
                    infobloxAuto()
                elif len(a_record_ips) == len(a_record_names):
                    aRecordAdd(a_record_ips,a_record_names)
                else:
                    # raise an error explaining not enough names were added
                    aRecord()
            else:
                try:
                    ipaddress.ip_address(record_IP)
                    a_record_ips.append(record_IP)
                    while True:
                        print('What is the domain name of the A record?')
                        record_name = input('> ') + infoblox_zone
                        if record_name == '':
                            continue    # Can't enter an IP without a domain name ;)
                        else:
                            a_record_names.append(record_name)
                            break
                except ValueError:
                    print('Please enter a valid IP address')
                    continue
    elif int(user_choice) == 2:
        print('''
            ***************************************************************************************
            **** NOTE: After entering the final record deletion, just press [ENTER] to proceed ****
            ***************************************************************************************
            ''')
        while True:
            print('What is the IP address of the A record?')
            record_IP = input('> ')
            if record_IP == '':
                if len(a_record_ips) < 1:
                    print('\nReturning to Main Menu!\n')
                    infobloxAuto()
                elif len(a_record_ips) == len(a_record_names):
                    aRecordDelete(a_record_ips,a_record_names)
                else:
                    # raise an error explaining not enough names were added
                    aRecord()
            else:
                try:
                    ipaddress.ip_address(record_IP)
                    req_params = {'ipv4addr':record_IP}
                    r = requests.get(
                        wapi_url + 'record:a',
                        params=req_params,
                        auth=(infoblox_username,
                            infoblox_password),
                        verify=False,
                        )
                    results = r.json()
                    backend_list = []
                    for result in results:
                        backend_list.append(result['name'])
                    if len(backend_list) < 1:
                        print('There are no matching A records')
                        time.sleep(3)
                        aRecord()
                    else:
                        os.system('cls')
                        print('The following A records exist for IP %s:\n' % (record_IP))
                        x = 0
                        while x < len(backend_list):
                            print('%s. %s' % (x + 1,backend_list[x]))
                            x += 1
                        print('\nWhich record would you like to remove?')
                        user_choice = int(input('> ')) - 1
                        a_record_ips.append(record_IP)
                        a_record_names.append(backend_list[user_choice])
                except ValueError:
                    print('Please enter a valid IP address')
                    continue
    elif int(user_choice) == 3:
        infobloxAuto()
    else:
        print('\nInvalid selection!')
        aRecord()

def aRecordAdd(ips,names):
    os.system('cls')
    print('''
        **************************************************************************************
        ****** Please press [ENTER] to confirm the addition of the following record(s): ******
        **************************************************************************************
        ''')
    x = 0
    while x < len(ips):
        print(str(x + 1) + '. ' + ips[x] + ' - ' + names[x])
        x += 1
    user_choice = input('> ')
    if user_choice == '':
        y = 0
        while y < len(ips):
            new_record = objects.ARecordBase.create(conn, check_if_exists=False, ip=ips[y], name=names[y])
            y += 1
        print('\n%s Records have been added' % (len(ips)))
        time.sleep(3)
        infobloxAuto()
    else:
        print('Addition canceled!')
        time.sleep(3)
        aRecord()

def aRecordDelete(ips,names):
    os.system('cls')
    print('''
        **************************************************************************************
        ****** Please press [ENTER] to confirm the deletion of the following record(s): ******
        **************************************************************************************
        ''')
    x = 0
    while x < len(ips):
        print(str(x + 1) + '. ' + ips[x] + ' - ' + names[x])
        x += 1
    user_choice = input('> ')
    if user_choice == '':
        y = 0
        while y < len(ips):
            delete_record = objects.ARecordBase.search(conn, ip=ips[y], name=names[y])
            delete_record.delete()
            y += 1
        print('\n%s Records have been deleted' % (len(ips)))
        time.sleep(3)
        infobloxAuto()
    else:
        print('Deletion canceled!')
        time.sleep(3)
        aRecord()

def cnameRecord():
    x = 0
    cname_record_names = []
    cname_record_canonicals = []
    os.system('cls')
    print('[CNAME Record] Please make a selection:')
    print('1. Record Addition')
    print('2. Record Removal')
    print('3. Return to Infoblox Menu')
    user_choice = input('> ')
    if int(user_choice) == 1:
        print('''
            ***************************************************************************************
            **** NOTE: After entering the final record addition, just press [ENTER] to proceed ****
            ***************************************************************************************
            ''')
        while True:
            print('What is the domain name of the CNAME record (do not include \'umd.edu\')?')
            record_name = input('> ') + infoblox_zone
            if record_name == infoblox_zone:
                if len(cname_record_names) < 1:
                    print('''
                        Returning to prior menu!
                        ''')
                    cnameRecord()
                elif len(cname_record_names) == len(cname_record_canonicals):
                    print(cname_record_names)
                    cnameRecordAdd(cname_record_names,cname_record_canonicals)
                else:
                    # raise an error explaining not enough names were added
                    cnameRecord()
            else:
                cname_record_names.append(record_name)
                req_params = {'name':record_name}
                r = requests.get(
                    wapi_url + 'record:cname',
                    params=req_params,
                    auth=(infoblox_username,
                        infoblox_password),
                    verify=False)
                existing_cname = []
                existing_cname.append(objects.CNAMERecord.search(conn, name=record_name))
                if existing_cname == [None]:
                    print('What is the canonical FQDN of the CNAME record?')
                    canonical_name = input('> ')
                    if canonical_name == '':
                        continue    # Can't enter a name without an alias ;)
                    else:
                        cname_record_canonicals.append(canonical_name)
                        continue
                else:
                    print('A CNAME for record %s already exists.' % (record_name,))
                    time.sleep(3)
                    cnameRecord()
    elif int(user_choice) == 2:
        print('''
            ***************************************************************************************
            **** NOTE: After entering the final record deletion, just press [ENTER] to proceed ****
            ***************************************************************************************
            ''')
        while True:
            print('What is the domain name of the CNAME record (do not include \'umd.edu\')')
            record_name = input('> ') + infoblox_zone
            if record_name == infoblox_zone:
                if len(cname_record_names) < 1:
                    print('\nReturning to Main Menu!\n')
                    infobloxAuto()
                elif len(cname_record_names) == len(cname_record_canonicals):
                    cnameRecordDelete(cname_record_names,cname_record_canonicals)
                else:
                    # raise an error explaining not enough names were added
                    aRecord()
            else:
                req_params = {'name':record_name}
                r = requests.get(
                    wapi_url + 'record:cname',
                    params=req_params,
                    auth=(infoblox_username,
                        infoblox_password),
                    verify=False,
                    )
                results = r.json()
                backend_list = []
                for result in results:
                    backend_list.append(result['name'])
                if len(backend_list) < 1:
                    print('There are no matching CNAME records')
                    time.sleep(3)
                    cnameRecord()
                else:
                    os.system('cls')
                    print('Press [ENTER] to delete domain name:\n\n%s\n' % (record_name,))
                    user_choice = input('> ')
                    if user_choice == '':
                        delete_record = objects.CNAMERecord.search(conn, name=record_name)
                        delete_record.delete()
                        print('Record has been deleted')
                        time.sleep(3)
                        cnameRecord()
                    else:
                        cnameRecord()
    elif int(user_choice) == 3:
        infobloxAuto()
    else:
        cnameRecord()

def cnameRecordAdd(names,canonicals):
    os.system('cls')
    print('''
        **************************************************************************************
        ****** Please press [ENTER] to confirm the addition of the following record(s): ******
        **************************************************************************************
        ''')
    x = 0
    while x < len(names):
        print(str(x + 1) + '. ' + names[x] + ' - ' + canonicals[x])
        x += 1
    user_choice = input('\n> ')
    if user_choice == '':
        y = 0
        while y < len(names):
            new_record = objects.CNAMERecord.create(conn, name=names[y], canonical=canonicals[y])
            y += 1
        if len(names) == 1:
            print('\n%s Record has been added' % (len(names)))
            time.sleep(3)
            infobloxAuto()
        else:
            print('\n%s Records have been added' % (len(names)))
            time.sleep(3)
            infobloxAuto()
    else:
        print('Addition canceled!')
        time.sleep(3)
        cnameRecord()

def cnameRecordDelete(names,canonicals):
    os.system('cls')
    print('''
        **************************************************************************************
        ****** Please press [ENTER] to confirm the deletion of the following record(s): ******
        **************************************************************************************
        ''')
    x = 0
    while x < len(names):
        print(str(x + 1) + '. ' + names[x] + ' - ' + canonicals[x])
        x += 1
    user_choice = input('> ')
    if user_choice == '':
        y = 0
        while y < len(names):
            delete_record = objects.CNAMERecord.search(conn, name=names[y], canonical=canonicals[y])
            delete_record.delete()
            y += 1
        print('\n%s Records have been deleted' % (len(names)))
        time.sleep(3)
        infobloxAuto()
    else:
        print('Deletion canceled!')
        time.sleep(3)
        cnameRecord()

def txtRecord():
    x = 0
    txt_record_names = []
    txt_record_texts = []
    os.system('cls')
    print('[TXT Record] Please make a selection:')
    print('1. Record Addition')
    print('2. Record Removal')
    print('3. Return to Infoblox Menu')
    user_choice = input('> ')    
    if int(user_choice) == 1:
        print('''
            ***************************************************************************************
            **** NOTE: After entering the final record addition, just press [ENTER] to proceed ****
            ***************************************************************************************
            ''')
        while True:
            print('What is the domain name of the TXT record (do not include \'umd.edu\')?')
            record_name = input('> ') + infoblox_zone
            txt_record_names.append(record_name)
            if record_name == '':
                if len(txt_record_names) < 1:
                    print('\nReturning to Main Menu!\n')
                    time.sleep(3)
                    infobloxAuto()
                elif len(txt_record_names) == len(txt_record_texts):
                    txtRecordAdd(txt_record_names,txt_record_texts)
                else:
                    # raise an error explaining not enough names were added
                    txtRecord()
            else:
                while True:
                    print('What is the text for the TXT record?')
                    record_text = input('> ')
                    if record_name == '':
                        continue    # Can't enter an IP without a domain name ;)
                    else:
                        txt_record_texts.append(record_text)
    elif int(user_choice) == 2:
        print('''
            ***************************************************************************************
            **** NOTE: After entering the final record deletion, just press [ENTER] to proceed ****
            ***************************************************************************************
            ''')
        while True:
            print('What is the IP address of the A record?')
            record_IP = input('> ')
            if record_IP == '':
                if len(a_record_ips) < 1:
                    print('\nReturning to Main Menu!\n')
                    infobloxAuto()
                elif len(a_record_ips) == len(a_record_names):
                    aRecordDelete(a_record_ips,a_record_names)
                else:
                    # raise an error explaining not enough names were added
                    aRecord()
            else:
                try:
                    ipaddress.ip_address(record_IP)
                    req_params = {'ipv4addr':record_IP}
                    r = requests.get(
                        wapi_url + 'record:a',
                        params=req_params,
                        auth=(infoblox_username,
                            infoblox_password),
                        verify=False,
                        )
                    results = r.json()
                    backend_list = []
                    for result in results:
                        backend_list.append(result['name'])
                    if len(backend_list) < 1:
                        print('There are no matching A records')
                        time.sleep(3)
                        aRecord()
                    else:
                        os.system('cls')
                        print('The following A records exist for IP %s:\n' % (record_IP))
                        x = 0
                        while x < len(backend_list):
                            print('%s. %s' % (x + 1,backend_list[x]))
                            x += 1
                        print('\nWhich record would you like to remove?')
                        user_choice = int(input('> ')) - 1
                        a_record_ips.append(record_IP)
                        a_record_names.append(backend_list[user_choice])
                except ValueError:
                    print('Please enter a valid IP address')
                    continue
    elif int(user_choice) == 3:
        infobloxAuto()
    else:
        print('\nInvalid selection!')
        aRecord()

################################################################################
#############################    Initial Function   ############################
################################################################################

def mainMenu():
    os.system('cls')
    print('1. Infoblox DNS')
    print('2. NoCut legacy')
    print('3. Exit')
    while True:
        try:
            user_choice = input('> ')
            if int(user_choice) == 1:
                infobloxAuto()
            elif int(user_choice) == 2:
                noCut()
            elif int(user_choice) == 3:
                sys.exit('Exiting the program!')
            else:
                print('\nInvalid selection!\n')
                continue
        except ValueError:
            print('\nInvalid selection!')
            continue

requests.packages.urllib3.disable_warnings() # suprress irrelevant messages to enduser
# logging.basicConfig(level=logging.DEBUG) # for debugging purposes. Remove in prod
mainMenu()



