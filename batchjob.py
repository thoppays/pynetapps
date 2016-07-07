#!/usr/bin/python

##batchjob.py

import pexpect
import re
import time
import cStringIO
import cgi
form = cgi.FieldStorage()

def gettime():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def runexp(user, password, device, command, dtype):
    response = cStringIO.StringIO()
    if dtype:
        prompt = re.compile('%s.*[>#]' % device.split('.')[0], re.IGNORECASE)
    else:
        prompt = re.compile('[$]')
    try:
        ## print " === SCRIPT LOG FOR %s === " % device
        print '\n%s => Connecting to %s' % (gettime(), device)
        # Log in to device
        ssh = pexpect.spawn('ssh %s@%s -o ConnectTimeout=10' % (user, device))
        preauth = ssh.expect([pexpect.TIMEOUT, 'yes/no', 'assword'])
        if preauth == 1:
                ssh.sendline('yes')
                ssh.expect('assword')
        ssh.sendline(password)
        postauth = ssh.expect([pexpect.TIMEOUT, prompt])
        if dtype:
            ssh.sendline('enable')
            e = ssh.expect([prompt, 'word'])
            if e == 1:
                ssh.sendline(password)
                ssh.expect(prompt)
                ssh.sendline('term len 0')
                ssh.expect(prompt)

        ssh.logfile = response
        ssh.sendline('')
        ssh.expect(prompt)
        print '%s => Applying configuration to %s' %(gettime(), device)
        # Send each line in configuration file
        for line in command:
            ssh.sendline(line)
            print "Running %s" % line
            if dtype:
                ssh.expect('[>#]')
            else:
                ssh.expect('[$]')
        ssh.close()
        print '%s => Completed and closed the connection to %s' %(gettime(), device)
        return response
##    except pexpect.exceptions.TIMEOUT:
    except:
        print "%s => Unable to contact the device %s. Here is what I got ==" %(gettime(), device)
        print ssh.before, ssh.after
        failures.append(device)
        return None
##    except pexpect.TIMEOUT:
##        print "%s => Script could not login. Here is what I got for %s ==" %(gettime(), device)
##        print ssh.before, ssh.after, "=="
##        failures.append(device)
##        return None
##    except pexpect.exceptions.EOF:
##        print "%s => Unable to contact the device %s. Here is what I got ==" %(gettime(), device)
##        print ssh.before, ssh.after
##        failures.append(device)
##        return None


## MAIN PROGRAM STARTS HERE ##

username = form.getvalue("user")
password = form.getvalue("pwd")
devlist = form.getvalue("devices")
cmdlist =  form.getvalue("commands")
devicetype = form.getvalue("devtype")
failures = []

devices = devlist.split("\r\n")
commands = cmdlist.split("\r\n")

for edevice in devices:
    if edevice is not "":
        if devicetype == "network":
            resp = runexp(username, password, edevice, commands, True)
        elif devicetype == "server":
            resp = runexp(username, password, edevice, commands, False)

        if resp is not None:
            ## print " === OUTPUT GENERATED FOR %s ===" % edevice
            print resp.getvalue()
        print 60*"~-"

if len(failures) > 0:
    print "%s => The script was unable to run on the following devices::" % gettime()
    for failure in failures:
        print failure
    print "Number of failed devices = %s" %len(failures)

### END OF SCRIPT
