#!/usr/bin/env python3
import requests
import getpass

# Set Hosts
atsProd = 'atsprod.wvu.edu'
soapProd = 'soaprod.wvu.edu'
mapProd = 'mapprod.wvu.edu'

# Set User Agents
firefox = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

# Set Accepts
html = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

# Set Languages
english = 'en-US,en;q=0.8'

# Set Encodings
gzip = 'gzip, deflate, br'

# Set Connections
alive = 'keep-alive'

# Set Referers
ats = 'https://atsprod.wvu.edu/sso/pages/maplogin.jsp'
swf = 'https://esd.wvu.edu/otl/OTL_TIMECARD.swf'
esd = 'https://esd.wvu.edu/flexotllinks/OTLLinks.swf?nocache=0.3090389143550235'

# Set Content Types
xml = 'text/xml; charset=utf-8'

session = requests.Session()

# Authenticate with MyAccess
def authenticate(username, password):
    r = session.post('https://atsprod.wvu.edu/sso/auth', 
    data = {
        'p_action':'OK', 
        'appctx':'', 
        'locale':'', 
        'p_cancel_url':'https%3A%2F%2Fmyapps.wvu.edu', 
        'site2pstoretoken':'v1.4~5246C911~E00D49D2D438B4AF71B1255D514F6A7D0B4FB47EF924655B9A4EF842C58B5520FF1708A135DCF39977EAC44308F2AED67A42994B3DBAC280F9D88CFC1257D07D51F0581998027A20F2BE74B380F626BA5DE60921650FD7CD65297286E5DEFF599B8382ACFD912F60D8967A48ABB2482B0311DCE6A6077A4CF104B76443F82007F0DD097712EFCCA3CC127EE39B374583F876A5DAA727C9A2B4EF8E9B44CDBAD05F9817FBDF2FC31778E8ECAFFD6DD0BDE2DABF71F0CAED80272684D6BCEA97FF', 
        'v':'v1.4',
        'ssousername':username, 
        'password':password}, 
    headers = {
        'Origin':'https://atsprod.wvu.edu',
        'User-agent':firefox,
        'Accept':html,
        'Accept-Language':english,
        'Accept-Encoding':gzip,
        'Connection':alive,
        'Referer':ats,
        'Content-Type':'application/x-www-form-urlencoded',
        'SOAPAction':'null'
    })

# Build And Send Requests To Get Person ID
def getPersonId(session):
    SSOData = session.get('https://soaprod.wvu.edu/WvuSSOEbizService/wvussoebizservice',
     headers = {
        'Origin':'https://' + soapProd,
        'User-agent':firefox,
        'Accept':html,
        'Accept-Language':english,
        'Accept-Encoding':'null',
        'Connection':alive,
        'Referer':esd,
        'Content-Type':'null',
        'SOAPAction':'null'})
    SSOText = str(SSOData.text)
    personId = SSOText[SSOText.find("<personId>")+10:SSOText.find("</personId>")]
    return personId

# Get the status WSDL, Response Needed For Setting The JSESSION Cookie
def getWSDL(session):
    WSDL = session.get('https://soaprod.wvu.edu/WvuOTLTimecardHeaderWs/GET_TIMECARD_HEADERSoapHttpPort?WSDL',
     headers = {
        'Origin':'https://' + soapProd,
        'User-agent':firefox,
        'Accept':html,
        'Accept-Language':english,
        'Accept-Encoding':gzip,
        'Connection':alive,
        'Referer':swf,
        'Content-Type':'null',
        'SOAPAction':'null'})
    return WSDL

username = input('Enter a username: ')
password = getpass.getpass('Enter a password: ')
auth = authenticate(username, password) #TODO check if authentication was successful
personId = getPersonId(session)
print('PersonId: ' + personId)
getWSDL()