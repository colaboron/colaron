import sys        
import subprocess, requests, json, time
import codecs, sys, os
from optparse import OptionParser



###     To view list of users use 'cat enrichment.csv | grep -v first_name | cut -d',' -f1 | sort | uniq'
###     or add wc -l at the end to count





def get_cw():
    """use with --cw=[CW] for a single cw, and get the script out of the for loop"""
    usage = "%prog [options]"
    parser = OptionParser(usage)
    parser.add_option('--cw', dest='cw',  help='''Mandatory. Cloudwell to connect to. ''')
    options, args = parser.parse_args()
    if not parser.values.cw:
            parser.print_help()
            print 'ERROR: Test case name is mandatory'
            sys.exit(1)

    return options.cw



#CSVCw = cw = get_cw()
cwl = [10, 11, 12, 13, 14, 15, 18, 19, 21, 22, 23, 25, 26, 28, 29, 30, 31, 32, 33, 34, 39, 40, 42, 43, 45] #list of production servers including VIP ones
#cwl = [20,35,36,37] #non-frozen staging cws
for cw in cwl:
    start = time.time()
    logger = codecs.open('/home/ron/Documents/email/enr%s.csv' % cw, mode='a', encoding='utf-8') #currently writes to a CSV file.
    cmd = 'ssh -T ubuntu@cw%s.colabo.com -o StrictHostKeyChecking=no -i ~ron/.ssh/stepwells_well-kp.pem -p 14422 -L%s:127.0.0.1:8080' % (cw, str(22212 + int(cw))) # NOTE THE KEY PATH. CURRENTLY SET TO RON'S COMPUTER
    proc = subprocess.Popen(cmd, env=os.environ, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    url = "http://localhost:%s/sql" % str(22212 + int(cw)) # make sure a tunnel isn't already opened in these ports. cw10 will open it on port 22222, so be careful
    sql = "select l.first_name, l.last_name,l.PERSONA_BM_STATUS,l.ANALYTICS_VERSION,c.COMPANY_BM_STATUS from sw_lead as l left join sw_company as c on l.company_id=c.id where (l.persona_bm_status!='COMPLETED' or c.company_bm_status!='COMPLETED' or l.analytics_version is null)"
    spayload = {'sql' : sql, 'user' :  '-- all users --', 'json' : '1'}
    resp  = requests.post(url, data=spayload)
    print 'sent sql request'
    jsonresp = json.loads(resp.text)
    print 'got json back'
    userlist = {}
    #BEGINNING OF SCRIPT CONTENT#
    for user in jsonresp:
        if 'test_' in user or 'projectstepwells' in user:
            continue
        for item in jsonresp[user]:
            if 'row' in item:
                logwrite = ''
                logwrite+='%s",' % user
                for oitem in jsonresp[user][item]:
                    logwrite += '"%s",' % oitem
                logger.write('"%s\n' % logwrite[:-1])


    #END OF SCRIPT CONTENT#            

            

    print 'done'
    logger.close
    end = time.time()
    print end - start
    proc.communicate(input='logout\n')
os.system('echo Username,first_name,last_name,persona_bm_status,analytics_version,company_bm_status > enrichment')
os.system('cat *.csv >> enrichment')
os.system('rm *.csv')
os.system('mv enrichment enrichment.csv')
