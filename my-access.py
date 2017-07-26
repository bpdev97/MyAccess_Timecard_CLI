#!/usr/bin/env python
import requests
import getpass

def authenticate(username, password):
    r = requests.post('https://atsprod.wvu.edu/sso/auth', data = {
        'p_action':'OK', 
        'appctx':'', 
        'locale':'', 
        'p_cancel_url':'https%3A%2F%2Fmyapps.wvu.edu', 
        'site2pstoretoken':'v1.4~5246C911~E00D49D2D438B4AF71B1255D514F6A7D0B4FB47EF924655B9A4EF842C58B5520FF1708A135DCF39977EAC44308F2AED67A42994B3DBAC280F9D88CFC1257D07D51F0581998027A20F2BE74B380F626BA5DE60921650FD7CD65297286E5DEFF599B8382ACFD912F60D8967A48ABB2482B0311DCE6A6077A4CF104B76443F82007F0DD097712EFCCA3CC127EE39B374583F876A5DAA727C9A2B4EF8E9B44CDBAD05F9817FBDF2FC31778E8ECAFFD6DD0BDE2DABF71F0CAED80272684D6BCEA97FF', 
        'v':'v1.4',
        'ssousername':username, 
        'password':password})

    if "<Response [200]>" in str(r):
        return "Authenticated!"
    else:
        return "Rejected!"

username = input('Enter a username: ')
password = getpass.getpass('Enter a password: ')
print(authenticate(username, password))
