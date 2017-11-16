#!/usr/bin/env python3
import requests, keyring, getpass, datetime, calendar, os, sys


# Set Hosts
atsProd = 'https://atsprod.wvu.edu'
soapProd = 'https:soaprod.wvu.edu'
mapProd = 'https://mapprod.wvu.edu'
esdProd = 'https://esd.wvu.edu'

# Set User Agents
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'

# Set Accepts
accepts = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'

# Set Languages
langs = 'en-US,en;q=0.8'

# Set Encodings
encodings = 'gzip, deflate, br'

# Set Connections
alive = 'keep-alive'

# Set Referers
ats = 'https://atsprod.wvu.edu/sso/pages/maplogin.jsp'
swf = 'https://esd.wvu.edu/otl/OTL_TIMECARD.swf'
esd = 'https://esd.wvu.edu/flexotllinks/OTLLinks.swf?nocache=0.3090389143550235'
clock = 'https://esd.wvu.edu/webclock/WVUClock.swf'

# Set Content Types
contentType = 'text/xml; charset=utf-8'

# Set SOAP Actions
getStatus = '\"http://wvumap/GET_TIMECARD_HEADER.wsdl/callGetTimecardHeader\"'
getTime = '\"http://wvuotlgettimecard/GET_TIMECARD_SERVICE.wsdl/callGetTimecard\"'
getName = '\"http://edu/wvu/common/WVU_LRS_GET_PERSON_DETAIL.wsdl/getPersonDetailXML\"'

# Show help menu if -h argument is specified
def helpMenu():
    if "-h" in sys.argv:
        print("""
		The purpose of this script is yet to be determined and will soon be filled in...
		""")
        exit()

# Gets credentials from user
def getCredentials():
    global username, password
    if "-u" in sys.argv:
        username = sys.argv[sys.argv.index("-u") + 1]
    elif "--username" in sys.argv:
        username = sys.argv[sys.argv.index("--username") + 1]
    else:
        username = raw_input('Enter a username: ')
    if "-p" in sys.argv:
        password = sys.argv[sys.argv.index("-p") + 1]
    elif "--password" in sys.argv:
        username = sys.argv[sys.argv.index("--password") + 1]
    elif "-r" in sys.argv or "--resetPass" in sys.argv:
        password = getpass.getpass("Enter a new password to be stored in keychain for further use: ")
        keyring.set_password("myaccess", username, password)
        exit(0)
    elif keyring.get_password("myaccess", username) is not None:
        password = keyring.get_password("myaccess", username)
    else:
        password = getpass.getpass("Enter a password to be stored in keychain for further use: ")
        keyring.set_password("myaccess", username, password)

# Create access session
session = requests.Session()

# Authenticate with MyAccess and return if successful
def authenticate():
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
        'User-agent':agent,
        'Accept':accepts,
        'Accept-Language':langs,
        'Accept-Encoding':encodings,
        'Connection':alive,
        'Referer':ats,
        'Content-Type':'application/x-www-form-urlencoded',
        'SOAPAction':'null'
    })

    # Check for authorization cookie
    if "_WL_AUTHCOOKIE_JSESSIONID" in session.cookies:
        return True
    else:
        return False

# Build And Send Requests To Get Person ID
def getPersonId(session):
    SSOData = session.get('https://soaprod.wvu.edu/WvuSSOEbizService/wvussoebizservice',
     headers = {
        'Origin':soapProd,
        'User-agent':agent,
        'Accept':accepts,
        'Accept-Language':langs,
        'Accept-Encoding':'null',
        'Connection':alive,
        'Referer':esd,
        'Content-Type':'null',
        'SOAPAction':'null'})
    SSOText = str(SSOData.text)
    personId = SSOText[SSOText.find("<personId>")+10:SSOText.find("</personId>")]
    return personId

# Set the JSESSION Cookie needed for Timecard related actions
def setJSESSIONTimecardCookie(session):
    request = session.get('https://soaprod.wvu.edu/WvuOTLTimecardHeaderWs/GET_TIMECARD_HEADERSoapHttpPort?WSDL',
     headers = {
        'Origin':soapProd,
        'User-agent':agent,
        'Accept':accepts,
        'Accept-Language':langs,
        'Accept-Encoding':encodings,
        'Connection':alive,
        'Referer':swf,
        'Content-Type':'null',
        'SOAPAction':'null'})

# Set the JSESSION Cookie needed for punching in and out and assign assignment
def setJSESSIONPunchCookie(session):
    request = session.get('https://esd.wvu.edu/WvuOTLSSOServices/wvuotlssoservlet?408',
     headers = {
        'User-agent':agent,
        'Accept':accepts,
        'Accept-Language':langs,
        'Accept-Encoding':encodings,
        'Connection':alive,
        'Referer':clock,
        'Content-Type':'null',
        'SOAPAction':'null'})
    
    # Parse out and return assignment
    requestStr = str(request.text)
    return requestStr[requestStr.find("<assignment>")+12:requestStr.find("</assignment>")]

# Build And Send Requests To Get TimeCard Status
def getTimeCardStatus(session, personId, startDate, endDate):
    # Set JSESSION cookie
    setJSESSIONTimecardCookie(session)
    # Generate SOAP Envelope
    soapData = buildSOAPStatusData (personId, startDate, endDate)
    # Send Request
    request = session.post('https://soaprod.wvu.edu/WvuOTLTimecardHeaderWs/GET_TIMECARD_HEADERSoapHttpPort',
      soapData,
      headers = {
        'Origin':soapProd,
        'User-agent':agent,
        'Accept':accepts,
        'Accept-Language':langs,
        'Accept-Encoding':'null',
        'Connection':alive,
        'Referer':swf,
        'Content-Type':contentType,
        'SOAPAction':getStatus
        })

    # Parse out and return status
    StatusText = str(request.text)
    return StatusText[StatusText.find("<ns0:employeeStatus>")+20:StatusText.find("</ns0:employeeStatus>")]

# Build And Send Requests To Get TimeCard Status
# TODO Make this function more useful????
def getTimeCardTimes(session, soapData):
    request = session.post('https://soaprod.wvu.edu/WvuOTLGetTimecardWs/GET_TIMECARD_SERVICESoapHttpPort',
      soapData,
      headers = {
        'Origin':soapProd,
        'User-agent':agent,
        'Accept':accepts,
        'Accept-Language':langs,
        'Accept-Encoding':'null',
        'Connection':alive,
        'Referer':swf,
        'Content-Type':contentType,
        'SOAPAction':getTime
        })
    return request

# Build And Send Requests To Punch in or out
def punch(session, personId, time, inOut):
    # Set JSESSION cookie and get assignment
    assignment = setJSESSIONPunchCookie(session)
    # Generate SOAP Envelope
    soapData = buildSOAPPunchData(personId, assignment, inOut, time)
    # Send Request
    request = session.post('https://esd.wvu.edu/WvuOTLClockService/WVU_OTL_WEB_CLOCKSoapHttpPort',
      soapData,
      headers = {
        'Origin':esdProd,
        'User-agent':agent,
        'Accept':'*/*',
        'Accept-Language':langs,
        'Accept-Encoding':encodings,
        'Connection':alive,
        'Referer':clock,
        'Content-Type':contentType
    })

    requestText = str(request.text)
    if requestText[requestText.find("<ns0:pstatusOut>")+12:requestText.find("</ns0:pstatusOut>")] == "100 - NORMAL":
        if inOut == "I":
            return "Successful clock in at " + time + "."
        else:
            return "Successful clock out at " + time + "."
    else:
        return requestText

# Builds SOAP Envelope For Timecard Status Request
def buildSOAPStatusData (personId, startDate, endDate):
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
    soapData = soapDataTemplate%(personId, startDate, endDate)
    return soapData

# Builds SOAP Envelope For Timecard Time Request
def buildSOAPTimesData (personId, startDate, endDate):
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
    soapData = soapDataTemplate%(personId, startDate, endDate)
    return soapData

# Builds SOAP Envelope For Punch Request
def buildSOAPPunchData(personId, assignment, inOut, time):
    soapDataTemplate = '''<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SOAP-ENV:Body xmlns:ns1="http://wvu_ats_dev/WVU_OTL_WEB_CLOCK.wsdl/types/">
    <ns1:callInsertClockTransactionElement>
      <ns1:pPersonId>%s</ns1:pPersonId>
      <ns1:pAssignmentNumber>%s</ns1:pAssignmentNumber>
      <ns1:pClockedTime>%s</ns1:pClockedTime>
      <ns1:pClockedType>%s</ns1:pClockedType>
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
    soapData = soapDataTemplate%(personId, assignment, time, inOut)
    return soapData

# Build dates dict with current, start, and end pay period dates
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

# Get Formatted Current Time
def getFormattedCurrentTime():
    return datetime.datetime.now().strftime("%Y-%m-%dT%X.000-04:00")

# Main
def main():
    helpMenu()
    getCredentials()
    if authenticate():
        personId = getPersonId(session)
        dates = getDates()
        # Check for punch argument
        if "-i" in sys.argv or "--in" in sys.argv:
            print(punch(session, personId, getFormattedCurrentTime(), "I"))
        elif "-o" in sys.argv or "--out" in sys.argv:
            print(punch(session, personId, getFormattedCurrentTime(), "O"))
    else:
        print('Invalid credentials! Consider resetting your keychain password with --resetPass if you have it setup')
        exit(1)
main()

# Left over functionality examples
# -----------------------------------
# timeCardStatus = getTimeCardStatus(session, personId, dates[1], dates[2])
# #timeCardTimes = getTimeCardTimes(session, buildSOAPTimesData(personId, dates[1], dates[2]))
