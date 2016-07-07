#!/usr/bin/python

## routcompwh.py
##Author: Saravana Thoppay (TVS)
## web version of routab_comp.py
import re
import sys
from datetime import datetime
import cStringIO
import cgi
form = cgi.FieldStorage()

def display_match(match, pos):
    if match is not None and pos == 0:
        return '%s' % (match.group()).strip()
    elif match is not None and pos == 1:
        return '%s' % (match.group(1)).strip()
    else:
        return None

def gettime():
    return datetime.today().strftime("%H:%M:%S.%f")

def routeparser(routes, dictout):
    print "%s => Started parsing" %gettime()
    for line in routes:
        if not (len(line) == 1):
            try:
                code = display_match(reCodes.search(line), 0)
                # print code
                prefix = display_match(rePrefix.search(line), 0)
                # print prefix
                next_hop = display_match(reNexthop.search(line), 0)
                # print next_hop
                # Cleaning up the next hop string
                if next_hop is not None:
                    next_hop = next_hop.replace(',','')
                admetric = display_match(reAdMetric.search(line), 1)
                # print admetric
                # Splitting Admin Distance and Metric and assigning to variables
                if admetric is not None:
                    ad , metric = admetric.split('/')
                elif admetric is None:
                    ad , metric = None, None
                else:
                    print "%s => Error Occured while splitting AD & Metric" %gettime()
                    break
                age = display_match(reAge.search(line), 0)
                subnets = display_match(reSubnetted.search(line), 1)
                interface = display_match(reInterface.search(line), 1)
                if (prefix is not None) and (subnets is None):
                    holdcode = code
                    holdprefix = prefix
                    dictout[prefix] = [[code, next_hop, ad, metric, age, interface, subnets]]
                    ## print code, prefix, next_hop, ad, metric, age, interface, subnets
                elif (prefix is not None) and (subnets is not None):
                    dictout['s'+prefix] = [[code, next_hop, ad, metric, age, interface, subnets]]
                elif next_hop is not None:
                    dictout[holdprefix].append([holdcode, next_hop, ad, metric, age, interface, subnets])
                    ## print holdcode, holdprefix, next_hop, ad, metric, age, interface, subnets
                else:
                    pass
            except:
                pass
##                print line
##                e = sys.exc_info()[0]
##                print "%s => Error Occured due to exceptions - %s" %(gettime(), e)
    print "%s => Ended parsing" %gettime()

def comp_attr(pre, post, pos):
    attr = codes[pos]
    for key, val in pre.items():
        if post.has_key(key):
            rtent = len(val)-1
            while rtent >= 0:
                if not pre[key][rtent][pos] == post[key][rtent][pos]:
                    kee=key.replace('s', '')                    
                    print "%s Changed for %s\tfrom %s ==> %s" \
                          %(attr, kee, val[rtent][pos], post[key][rtent][pos])
                rtent -= 1

def check_missing_routes(first, second):
    route_not_found = []
    for key, val in first.items():
        if not second.has_key(key):
            route_not_found.append(key)
    return route_not_found
    
def comp2table(pre, post, pos):
    attr = codes[pos]
    print '<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\">'
    print '<th>%s</th><th>%s</th><th>%s</th>' %("Prefix", "Pre-"+attr, "Post-"+attr)
    for key, val in pre.items():
        if post.has_key(key):
            rtent = len(val)-1
            while rtent >= 0:
                try:
                    if not pre[key][rtent][pos] == post[key][rtent][pos]:
                        kee=key.replace('s', '')
                        print '<tr>'
                        print '<td>%s</td><td style="color:red">%s</td><td>%s</td>' \
                              %(kee, val[rtent][pos], post[key][rtent][pos])
                        # print "%s Changed for %s\tfrom %s ==> %s" \
                              # %(attr, kee, val[rtent][pos], post[key][rtent][pos])
                        print '</tr>'
                    rtent -= 1
                except IndexError:
                    print pre[key][rtent][pos], key, rtent, pos
                    break
    print "</table>\n<br>\n<br>"

def gateway_chk(ilist):
    for line in ilist:
        if line.startswith('Gateway'):
            return line

### MAIN PROGRAM STARTS HERE ###
# fields = form.getvalue("field_to_comp")
rtpre =  form.getvalue("preroutes")
rtpos = form.getvalue("postroutes")
response = cStringIO.StringIO()

# field = int(fields)
routespre = rtpre.split("\r\n")
routespos = rtpos.split("\r\n")

reCodes = re.compile('^(([A-Z]\s)|([A-Z]\*))[A-Z]*[\s]*')
rePrefix = re.compile('(([0-9]+\.){3,}[0-9]+(/[0-9]+)? )')
reNexthop = re.compile('(([0-9]+\.){3,}[0-9]+,)')
reAdMetric = re.compile('\[(.*)\]')
reAge = re.compile('(([0-9]+:)+[0-9]+)|([0-9]+(w|d)[0-9]+(d|h))')
reSubnetted = re.compile('subnetted, (\S+) subnets')
reInterface = re.compile(',\s(\S+(thernet|channel|oopback|ull|erial).*)$')

dictpre = {}
dictpos = {}
codes = {0:"Routing Code",1:"Next-Hop",\
         2:"Admin Distance",3:"Metric",\
         4:"Age",5: "Interface",\
         6:"Number of Subnets"}
route_not_found_in_pre = []
route_not_found_in_pos = []

routeparser(routespre, dictpre)
routeparser(routespos, dictpos)

num_of_pre_subnetted = sum(len(x) for x in dictpre.values() if x[0][6] is not None)
num_of_pre_prefixes = len(dictpre)
num_of_pre_paths = sum(len(x) for x in dictpre.values() if x[0][1] is not None)
num_of_pos_subnetted = sum(len(x) for x in dictpos.values() if x[0][6] is not None)
num_of_pos_prefixes = len(dictpos)
num_of_pos_paths = sum(len(x) for x in dictpos.values() if x[0][1] is not None)

print 'Content-type: text/html\n\n'
print '<!DOCTYPE html>'
print '<html>'
print '<body>'
print '<title>Route Comparision</title>'
print '<font face="verdana" color="black" size="2">'
print '''<head>
<style>
table {
    border-collapse: collapse;
    border-color: dodgerblue;
    width: 50%;
}
th {
    text-align: justify;
    text-decoration: underline;
    letter-spacing: 1px;
    }
h1 {
    font-size: 20px;
}
hr {
    border-width: 2px;
    border-color: dodgerblue;
}
tr:nth-child(odd){background-color: #f2f2f2}
</style>
</head>'''
print '<h1><p style="color:darkblue"> SUMMARY OF REPORT </p></h1>'
print '<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\">'

print "<tr><th> PRE-CHANGE ROUTING TABLE: </th></th><th> </th></tr>"
print "<tr><td>Number of prefixes with variable subnets:</td><td>%s</td></tr>" %num_of_pre_subnetted
print "<tr><td>Total Number of prefixes in the table:</td><td>%s</td></tr>" %num_of_pre_prefixes
# print "<tr><td>Sum of paths for each prefixes:</td><td>%s</td></tr>" %num_of_pre_paths
print "<tr><th> POST-CHANGE ROUTING TABLE: </th></th><th> </th></tr>"
print "<tr><td>Number of prefixes with variable subnets:</td><td>%s</td></tr>" %num_of_pos_subnetted
print "<tr><td>Total Number of prefixes in the table:</td><td>%s</td></tr>" %num_of_pos_prefixes
# print "<tr><td>Sum of paths for each prefixes:</td><td>%s</td></tr>" %num_of_pos_paths
print "</table>\n<br><hr />"

# print 53*"~-"
# print comp_attr(dictpre, dictpos, field)
# print comp2table(dictpre, dictpos, field)
print '<h3><b><p style="color:darkblue">  CHANGES BETWEEN TWO ROUTING TABLES </p></b></h3>'

if gateway_chk(routespre) != gateway_chk(routespos):
    print '''<br>\n<table border="1" cellspacing="0" cellpadding="2">
<td style="color:red">Gateway of last resort do not match.</td>
</table>\n<br>\n<br>'''
    
for n in [0,1,2,3,5,6]:
    comp2table(dictpre, dictpos, n)

not_in_pos = check_missing_routes(dictpre, dictpos)
not_in_pre = check_missing_routes(dictpos, dictpre)
print "<br><hr />"

print '<h3><b><p style="color:darkblue"> COMPARISION OF MISSING ROUTES </p></b></h3>'
print '<table border=\"1\" cellspacing=\"0\" cellpadding=\"2\">'

# print 53*"~-"
print "<th> Routes not in pre-change: </th>"
print "<th> Routes not in post-change: </th>"
print "<tr><td>"
for line in not_in_pre:
    print line.replace('s', '')+"<br>"

print "</td>\n<td>"
# print 53*"~-"
for line in not_in_pos:
    print line.replace('s', '')+"<br>"

print "</td></tr>\n</table>\n<br><hr />\n</body>\n</html>"
    
# print 53*"~-"
# print 23*"~-"+"END OF REPORT "+23*"~-"
### END OF SCRIPT
