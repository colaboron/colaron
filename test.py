import subprocess, requests, json, time
import codecs, sys, os
from optparse import OptionParser
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



cw = get_cw()
start = time.time()
logger = codecs.open('./result%s.txt' % cw, mode='a', encoding='utf-8')
logger.write('START\n')
cmd = 'ssh -T ubuntu@cw%s.colabo.com -o StrictHostKeyChecking=no -i ~/.ssh/stepwells_well-kp.pem -p 14422 -L%s:127.0.0.1:8080' % (cw, str(22212 + int(cw)))
proc = subprocess.Popen(cmd, env=os.environ, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(5)
url = "http://localhost:%s/sql" % str(22212 + int(cw))
sql = "select * from sw_extracted_element_block where metadata_value in ('https://www.linkedin.com/in/gktech','https://www.linkedin.com/in/yiftahporat')"
spayload = {'sql' : sql, 'user' :  '-- all users --', 'json' : '1'}
retjson = requests.post(url, data=spayload).text
if 'row1' in retjson or 'row2' in retjson:
    print 'found'
    logger.write(retjson)
    logger.write('\n\n\n\n\n\n\n')
logger.write('END\n')
logger.close()
end = time.time()
print end - start
proc.communicate(input='logout\n')
