import sys        
import subprocess, requests, json, time
import codecs, sys, os
from optparse import OptionParser

#CSV VARIBLES
CSVUser = ""
CSVName = ""
CSVCompany = ""
CSVOldEmail = ""
CSVNewEmail = ""
CSVPersonaBmId = ""
CSVPersonaBmBlocks = ""
CSVCw = ""
CSVLinkMail = ""
#END CSV VARIABLES


#_____________________________________________________________________

def email_by_pid_null(user):
    "Returns a list of email addresses for leads without persona_bm_id that have email property" 
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    sql = "select EMAIL from sw_lead where persona_bm_id is null AND NOT EMAIL=''" 
    params = {'sql' : sql, 'user' : user}
    resp  = requests.post(url, data=params)
    html = resp.text
    if html.find('<td>') == -1:
        return ""
    html = html.split('<td>')
    filterlist = []
    bufferlist = []
    for item in html:
        filterlist.append(item.split('</tr>'))
    for item in filterlist:
        for oitem in item:
            if len(oitem) > 4 and len(oitem) < 50:
                bufferlist.append(oitem)
    return bufferlist
#_____________________________________________________________________
    

def resetcsv():
    global CSVUser, CSVName, CSVCompany, CSVOldEmail, CSVNewEmail, CSVPersonaBmId, CSVPersonaBmBlocks, CSVLinkMail
    CSVUser = ""
    CSVName = ""
    CSVCompany = ""
    CSVOldEmail = ""
    CSVNewEmail = ""
    CSVPersonaBmId = ""
    CSVPersonaBmBlocks = ""
    CSVLinkMail = ""

    
def property_by_pid(user, bmid, prop):
    propp = prop
    if propp == 'FULLEMAIL':
        propp = 'EMAIL'
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    sql = "select %s from sw_lead where persona_bm_id='%s'" % (propp, bmid)
    if bmid == "all":
        sql = "select %s from sw_lead" % propp
    params = {'sql' : sql, 'user' : user}
    resp  = requests.post(url, data=params)
    html = resp.text
    if html.find('<td>') == -1:
        return ""
    html = html.split('<td>')
    filterlist = []
    for item in html:
        filterlist.append(item.split('</tr>'))
    for item in filterlist:
        for oitem in item:
            if len(oitem) > 4 and len(oitem) < 50 and prop.upper()=='EMAIL' and oitem != '<tr>':
                return oitem.split('@')[1]
            if prop.upper()!='EMAIL' and len(oitem) < 50 and len(oitem) > 1 and oitem != '<tr>':
                return oitem
            if oitem == '?':
                return '?'
    
def fix_mail(mail, lst, logger):
    if mail == 'null' or mail is None or mail == '':
        return
    user = lst['user']
    fn = lst['fName']
    ln = lst['lName']
    if mail != 'null':
        mail = '%s' % mail
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    sql = "update sw_lead set EMAIL='%s' where FIRST_NAME=%s and LAST_NAME='%s'" % (mail, fn, ln)
    payload = {'user' : user, 'sql' : sql}
    print 'updating mail', payload
    logger.write('changed %s %s\'s email from null to %s on user %s\n' % (fn, ln, mail, user))
    tmp = requests.post(url, data=payload)


def run_email_guesser(paramslist, logger):
    global CSVNewEmail
    url = "http://localhost:%s/admin" % str(22212 + int(cw))
    retval = requests.get(url, params=paramslist).text
    print retval
    newmail = retval.split('Found Email: ')
    if (len(newmail) > 1):
        CSVNewEmail = newmail[1]
        fix_mail(newmail[1], paramslist, logger)
    else:
        CSVNewEmail = ""
    

def change_email_to_null(user, fName, lName, oldmail, logger):
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    sql = "update sw_lead set EMAIL=null where FIRST_NAME='%s' and LAST_NAME='%s'" % (fName, lName)
    params= {'user' : user, 'sql' : sql}
    r = requests.post(url, data=params)
    logger.write('changed %s %s\'s email from %s to null on user %s\n' % (fName, lName, oldmail, user))
  

def email_by_id(user, bmid):
    url = "http://localhost:%s/admin" % str(22212 + int(cw))
    payload = {'cmd' : "blocksForBookmark", 'scenario' : bmid, 'user' : user}
    resp  = requests.post(url, data=payload)
    try:
        jsonlist = json.loads(resp.text)
    except ValueError:
        return True
    else:
        for item in jsonlist:
            if item['metadataKey'] == 'lead_email':
                return False
                
    return True


def logify_property_by_pid(user, bmid, prop):
    propp = prop
    lstl = []
    if propp == 'FULLEMAIL':
        propp = 'EMAIL'
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    sql = "select %s from sw_lead where persona_bm_id='%s'" % (propp, bmid)
    if bmid == "all":
        sql = "select %s from sw_lead" % propp
    params = {'sql' : sql, 'user' : user}
    resp  = requests.post(url, data=params)
    html = resp.text
    if html.find('<td>') == -1:
        return ""
    html = html.split('<td>')
    filterlist = []
    for item in html:
        filterlist.append(item.split('</tr>'))
    for item in filterlist:
        for oitem in item:
            if  (len(oitem) > 4 and len(oitem) < 50  or len(oitem) == 0)and prop.upper()=='EMAIL' and oitem != '<tr>':
                lstl.append(oitem.split('@')[1])
            if prop.upper()!='EMAIL' and (len(oitem) < 50 and len(oitem) > 1 or len(oitem) == 0) and oitem != '<tr>':
                lstl.append(oitem)
            if oitem == '?':
                return '?'
    return lstl


def logify_property_by_id(user, ID, prop):
    print 'start logify property by id'
    propp = prop
    lstl = []
    if propp == 'FULLEMAIL':
        propp = 'EMAIL'
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    sql = "select %s from sw_lead where ID='%s'" % (propp, ID)
    if ID == "all":
        sql = "select %s from sw_lead" % propp
    params = {'sql' : sql, 'user' : user}
    resp  = requests.post(url, data=params)
    html = resp.text
    if html.find('<td>') == -1:
        return []
    html = html.split('<td>')
    filterlist = []
    for item in html:
        filterlist.append(item.split('</tr>'))
    for item in filterlist:
        for oitem in item:
            if  (len(oitem) > 4 and len(oitem) < 50  or len(oitem) == 0)and prop.upper()=='EMAIL' and oitem != '<tr>':
                print 'DEBUG', oitem
                lstl.append(oitem.split('@')[1])
            if prop.upper()!='EMAIL' and (len(oitem) < 50 and len(oitem) > 1 or len(oitem) == 0) and oitem != '<tr>':
                lstl.append(oitem)
            if oitem == '?':
                return '?'
    print 'printing list', lstl
    return lstl



def iduser(user):
    url = "http://localhost:%s/sql" % str(22212 + int(cw))
    spayload = {'sql' : 'select ID from sw_lead where persona_bm_id is null', 'user' :  user}
    resp  = requests.post(url, data=spayload)
    html = resp.text
    if html.find('<td>') == -1:
        return []
    html = html.split('<td>')
    filterlist = []
    bufferlist = []
    for item in html:
        filterlist.append(item.split('</tr>'))
    for item in filterlist:
        for oitem in item:
            if oitem.isdigit():
                bufferlist.append(oitem)
    if len(bufferlist) > 0:
        filterlist.append({user:bufferlist})
    return filterlist



def logify_v2(user, value):
    global CSVUser, CSVName, CSVLinkMail, CSVOldEmail, CSVCompany 
    CSVUser = user
    fin = logify_property_by_id(user, value, 'FIRST_NAME')
    lan = logify_property_by_id(user, value, 'LAST_NAME')
    try:
        CSVName = fin[0] + " " + lan[0]
    except:
        CSVName = 'None'
    CSVLinkMail = "No"
    try:
        CSVOldEmail = logify_property_by_id(user, value, 'FULLEMAIL')[0]
    except:
        CSVOldEmail = 'None'
    try:    
        CSVCompany = logify_property_by_id(user, value, 'COMPANY')[0]
    except:
        CSVCompany = "None"
    csvlog.write("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % (CSVUser, CSVName, CSVCompany, CSVOldEmail, CSVNewEmail, CSVPersonaBmId, CSVPersonaBmBlocks, CSVCw, CSVLinkMail))
    resetcsv()


def logify_nulls(user):
    global CSVPersonaBmId, CSVPersonaBmBlocks, CSVNewEmail
    idlst = iduser(user)
    for item in idlist:
        for IDN in item.values()[0]:
            CSVPersonaBmId = "No"
            CSVPersonaBmBlocks = "No"
            CSVNewEmail = "None"
            logify_v2(user, IDN)


def logify(user, bmid):
    global CSVUser, CSVName, CSVOldEmail, CSVCompany
    CSVUser = user
    fin = logify_property_by_pid(user, bmid, 'FIRST_NAME')
    lan = logify_property_by_pid(user, bmid, 'LAST_NAME')
    value = logify_property_by_pid(user, bmid, 'ID')
    print 'got first name, last name, id', fin, lan, value
    try:
        CSVName = fin[0] + " " + lan[0]
    except:
        CSVName = 'None'
    try:
        CSVCompany = logify_property_by_id(user, value, 'COMPANY')[0]
        print 'got company', CSVCompany
    except Exception as ex:
        CSVCompany = "None"
        print '------------------\n', str(ex), '---------------------\n'
    csvlog.write("\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"\n" % (CSVUser, CSVName, CSVCompany, CSVOldEmail, CSVNewEmail, CSVPersonaBmId, CSVPersonaBmBlocks, CSVCw, CSVLinkMail))
    resetcsv()

def get_cw():

    usage = "%prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--cw', dest='cw',  help='''Mandatory. Cloudwell to connect to. ''')
    options, args = parser.parse_args()
    if not parser.values.cw:
            parser.print_help()
            print 'ERROR: Test case name is mandatory'
            sys.exit(1)

    return options.cw



CSVCw = cw = get_cw()
start = time.time()
idlist = []
loglist = []
otherlist = []
idloglist = []
csvlog = codecs.open('/home/ron/Documents/email/stats/emailcleanup%s.csv' % cw, mode='a', encoding='utf-8')
csvlog.write('"User","Name","Email","Email_Guesser","Cloudwell"\n')
cmd = 'ssh -T ubuntu@cw%s.colabo.com -o StrictHostKeyChecking=no -i ~ron/.ssh/stepwells_well-kp.pem -p 14422 -L%s:127.0.0.1:8080' % (cw, str(22212 + int(cw)))
proc = subprocess.Popen(cmd, env=os.environ, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(5)
url = "http://localhost:%s/sql" % str(22212 + int(cw))
spayload = {'sql' : 'select * from sw_lead where email!=\'naama@colabo.com\' and email!=\'\' and persona_bm_id is not null and real_create_time > \'2015-09-04\'', 'user' :  '-- all users --', 'json' : '1'}
resp  = requests.post(url, data=spayload)
jsonresp = json.loads(resp.text)
for user in jsonresp:
    for key in jsonresp[user]:
        if 'row' in key:
            print 'mark'
            bmid = jsonresp[user][key][43]
            fname = jsonresp[user][key][1]
            lname = jsonresp[user][key][2]
            email = jsonresp[user][key][6]
            guess = email_by_id(user, bmid)
            csvlog.write('"%s","%s","%s","%s","%s"' % (user, fname + ' ' + lname, email, guess, cw))

print 'done'
csvlog.close()
end = time.time()
print end - start
proc.communicate(input='logout\n')
