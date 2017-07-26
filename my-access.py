#!/usr/bin/env python3
import requests, getpass, datetime, calendar, os, sys

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
clock = 'https://esd.wvu.edu/webclock/WVUClock.swf'

# Set Content Types
xml = 'text/xml; charset=utf-8'

# Set SOAP Actions
getStatus = '\"http://wvumap/GET_TIMECARD_HEADER.wsdl/callGetTimecardHeader\"'
getTime = '\"http://wvuotlgettimecard/GET_TIMECARD_SERVICE.wsdl/callGetTimecard\"'
getName = '\"http://edu/wvu/common/WVU_LRS_GET_PERSON_DETAIL.wsdl/getPersonDetailXML\"'


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

# Get the clock WSDL, Response Needed For Setting The JSESSION Cookie
def getWSDLClock(session):
    WSDL = session.get('https://esd.wvu.edu/WvuOTLSSOServices/wvuotlssoservlet?408',
     headers = {
        'User-agent':firefox,
        'Accept':html,
        'Accept-Language':english,
        'Accept-Encoding':gzip,
        'Connection':alive,
        'Referer':clock,
        'Content-Type':'null',
        'SOAPAction':'null'})
    return WSDL

# Build And Send Requests To Get TimeCard Status
def getTimeCardStatus(session, soapData):
    status = session.post('https://soaprod.wvu.edu/WvuOTLTimecardHeaderWs/GET_TIMECARD_HEADERSoapHttpPort',
      soapData,
      headers = {
        'Origin':'https://' + soapProd,
        'User-agent':firefox,
        'Accept':html,
        'Accept-Language':english,
        'Accept-Encoding':'null',
        'Connection':alive,
        'Referer':swf,
        'Content-Type':xml,
        'SOAPAction':getStatus
        })

    StatusText = str(status.text)
    return StatusText[StatusText.find("<ns0:employeeStatus>")+20:StatusText.find("</ns0:employeeStatus>")]

# Build And Send Requests To Get TimeCard Status
def getTimeCardTimes(session, soapData):
    times = session.post('https://soaprod.wvu.edu/WvuOTLGetTimecardWs/GET_TIMECARD_SERVICESoapHttpPort',
      soapData,
      headers = {
        'Origin':'https://' + soapProd,
        'User-agent':firefox,
        'Accept':html,
        'Accept-Language':english,
        'Accept-Encoding':'null',
        'Connection':alive,
        'Referer':swf,
        'Content-Type':xml,
        'SOAPAction':getTime
        })

    return times

# Build And Send Requests To clock out
def clockOut(session, soapData):
    status = session.post('https://esd.wvu.edu/WvuOTLClockService/WVU_OTL_WEB_CLOCKSoapHttpPort',
      soapData,
      headers = {
        'Origin':'https://https://esd.wvu.edu',
        'User-agent':firefox,
        'Accept':'*/*',
        'Accept-Language':english,
        'Accept-Encoding':gzip,
        'Connection':alive,
        'Referer':clock,
        'Content-Type':xml
    })

    return status

# Builds SOAP Envelope For Status Request
def buildSOAPStatusData (personID, startDate, endDate):
    soapDataTemplate = '''<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <tns0:callGetTimecardHeaderElement xmlns:tns0="http://wvumap/GET_TIMECARD_HEADER.wsdl/types/">
      <tns0:pPersonId>%s</tns0:pPersonId>
      <tns0:pPeriodStartDate>%s</tns0:pPeriodStartDate>
      <tns0:pPeriodEndDate>%s</tns0:pPeriodEndDate>
      <tns0:pAssignmentId>-1</tns0:pAssignmentId>
      <tns0:pSupervisorId>-1</tns0:pSupervisorId>
      <tns0:pAttribute1 xsi:nil="true"/>
      <tns0:pAttribute2 xsi:nil="true"/>
      <tns0:pAttribute3 xsi:nil="true"/>
    </tns0:callGetTimecardHeaderElement>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''
    soapData = soapDataTemplate%(personID, startDate, endDate)
    return soapData

# Builds SOAP Envelope For Times Request
def buildSOAPTimesData (personID, startDate, endDate):
    soapDataTemplate = '''<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body>
    <tns0:callGetTimecardElement xmlns:tns0="http://wvuotlgettimecard/GET_TIMECARD_SERVICE.wsdl/types/">
      <pPersonId>%s</pPersonId>
      <pPeriodStartDate>%s</pPeriodStartDate>
      <pPeriodEndDate>%s</pPeriodEndDate>
      <pAssignmentId>-1</pAssignmentId>
      <pAttribute1 xsi:nil="true"/>
      <pAttribute2 xsi:nil="true"/>
      <pAttribute3 xsi:nil="true"/>
    </tns0:callGetTimecardElement>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''
    soapData = soapDataTemplate%(personID, startDate, endDate)
    return soapData

# Builds SOAP Envelope For Times Request
def buildSOAPClockData(personID, time):
    soapDataTemplate = '''<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body xmlns:ns1="http://wvu_ats_dev/WVU_OTL_WEB_CLOCK.wsdl/types/">
    <ns1:callInsertClockTransactionElement>
      <ns1:pPersonId>%s</ns1:pPersonId>
      <ns1:pAssignmentNumber>02 Seery, Marc H</ns1:pAssignmentNumber>
      <ns1:pClockedTime>%s</ns1:pClockedTime>
      <ns1:pClockedType>O</ns1:pClockedType>
      <ns1:pBadgeNumber></ns1:pBadgeNumber>
      <ns1:pGuid></ns1:pGuid>
      <ns1:pSourceType>W</ns1:pSourceType>
      <ns1:pSourceIdn>10.255.69.251</ns1:pSourceIdn>
      <ns1:pAttr1></ns1:pAttr1>
      <ns1:pAttr2></ns1:pAttr2>
      <ns1:pAttr3></ns1:pAttr3>
      <ns1:pAttr4></ns1:pAttr4>
      <ns1:pAttr5></ns1:pAttr5>
    </ns1:callInsertClockTransactionElement>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''
    soapData = soapDataTemplate%(personID, time)
    return soapData

def getDates():
    dates = []
    # Get The Current Date
    now = datetime.datetime.now()
    year = str(now.year)
    month =  str(now.month)
    day = str(now.day)
    # Get The Last Day Of The Month
    lastDayOfMonth = str(calendar.monthrange(now.year,now.month)[1])
    # Add A Zero If Month Or Day Is Only One Character
    if len(month) == 1:
        month = '0' + month
    if len(day) == 1:
        day = '0' + day
    # Put The Dates In XML Date Data Type Format
    if (now.day >= 1 and now.day <= 15):
        startDate = year + '-' + month + '-' + '01Z'
        endDate = year + '-' + month + '-' + '15Z'
    else:
        startDate = year + '-' + month + '-' + '16Z'
        endDate = year + '-' + month + '-' + lastDayOfMonth + 'Z'
    currentDate = year + '-' + month + '-' + day + 'Z'
    # Add The Dates To A List
    dates.append(currentDate)
    dates.append(startDate)
    dates.append(endDate)
    return dates

def getFormattedCurrentTime():
    return datetime.datetime.now().strftime("%Y-%m-%dT%X.000-04:00")

# What happens when script is run...
username = input('Enter a username: ')
password = getpass.getpass('Enter a password: ')
auth = authenticate(username, password) #TODO check if authentication was successful
personId = getPersonId(session)
#getWSDL(session)
dates = getDates()
timeCardStatus = getTimeCardStatus(session, buildSOAPStatusData(personId, dates[1], dates[2]))
print('----------------------')
print('PersonId: ' + personId)
print('Timecard Status: ' + timeCardStatus)
timeCardTimes = getTimeCardTimes(session, buildSOAPTimesData(personId, dates[1], dates[2]))
print(timeCardTimes.text)
print()
print('----------------')
a = getWSDLClock(session)
print(a.headers)
print(a.text)
print(clockOut(session, buildSOAPClockData(personId, getFormattedCurrentTime())).text)

#datetime.datetime.now().replace(hour=15, minute = 0, second = 0).strftime("%Y-%m-%dT%X.000-04:00")