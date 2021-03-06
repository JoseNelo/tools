#!/usr/bin/python
# @Author: Aldo Sotolongo
# @Date:   2016-05-25T14:22:59-04:00
# @Email:  aldenso@gmail.com
# @Last modified by:   Aldo Sotolongo
# @Last modified time: 2016-08-31T13:45:59-04:00
# File: filesystemalert.py
# Description: This script is useful to set filesystem alerts based on
# defined thresholds

from subprocess import Popen, PIPE
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib

fromaddr = "root@localhost"
toaddrs = "aldo@localhost"
# toaddrs=["aldo@localhost","aldo@aldoca.com","aldenso@gmail.com"]

# Set thresholds
yellow = 85
orange = 90
red = 95
# FS in alert
fsalert = []

filesystems = set()
cmd = "lsblk"
p = Popen(cmd, stdout=PIPE, shell=True)
output, error = p.communicate()
for line in output.splitlines():
    if len(line.split()) == 7:
        filesystems.add(line.split()[6])
for i in filesystems.copy():
    if i == '[SWAP]' or i == 'MOUNTPOINT':
        filesystems.remove(i)


def checkusage(filesystems):
    for fs in filesystems:
        cmd = "df {} | tail -1".format(fs)
        p = Popen(cmd, stdout=PIPE, shell=True)
        output, error = p.communicate()
        usage = int(output.split()[4][:-1])
        if usage >= yellow and usage < orange:
            print("{}:YELLOW ALERT".format(fs))
            fsalert.append(("YELLOW ALERT", fs, usage))
        elif usage >= orange and usage < red:
            print("{}:ORANGE ALERT".format(fs))
            fsalert.append(("ORANGE ALERT", fs, usage))
        elif usage >= red:
            print("{}:RED ALERT".format(fs))
            fsalert.append(("RED ALERT", fs, usage))
        else:
            print("{}:normal usage".format(fs))


def sendmail(fsalert):
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddrs
    msg['Subject'] = "FileSystem Alert"
    body = "{}".format(fsalert)
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()

    server = smtplib.SMTP('localhost')
    # server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, text)
    server.quit()


def main():
    checkusage(filesystems)
    if len(fsalert) != 0:
        sendmail(fsalert)
    else:
        print("Nothing to report")

if __name__ == "__main__":
    main()
