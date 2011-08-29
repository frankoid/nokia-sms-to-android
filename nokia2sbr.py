#!/usr/bin/env python
# Copyright Francis Devereux 2011

"""Converts SMS message data from Nokia PC Suite CSV format to SMS Backup and
Restore for Android (by Ritesh Sahu)

Useful for transferring SMSes from Nokia phones to Android phones"""

import csv, time, sys

from optparse import OptionParser
from xml.dom.minidom import Document

def nok_time_to_java_time(nok_time):
    nok_format = '%Y.%m.%d %H:%M'
    posix_time = time.mktime(time.strptime(nok_time, nok_format))
    java_time = posix_time * 1000
    return java_time

class SMS:
    def read_from_nok_csv_row(self, csv_row):
      self.valid = csv_row and csv_row[0] == 'sms'
      if not self.valid:
          return
      if csv_row[1] == 'deliver':
          self.direction = 'received'
          self.other_party = csv_row[2]
      elif csv_row[1] == 'submit':
          self.direction = 'sent'
          self.other_party = csv_row[3]
      elif 'SENT' in csv_row[1] or 'sent' in csv_row[1]:
          self.direction = 'sent'
          self.other_party = csv_row[3]
      elif 'RECEIVED' in csv_row[1] or 'received' in csv_row[1]:
          self.direction = 'received'
          self.other_party = csv_row[2]
      self.java_time = nok_time_to_java_time(csv_row[5])
      self.body = csv_row[7]

    def populate_sbr_element(self, sms_el):
        sms_el.setAttribute('address', self.other_party)
        sms_el.setAttribute('date', '%d' % self.java_time)
        if self.direction == 'received':
            t = '1'
        else:
            t = '2'
        sms_el.setAttribute('type', t)

        sms_el.setAttribute('body', self.body)
        sms_el.setAttribute('read', str(self.read))

        sms_el.setAttribute('protocol', '0')
        sms_el.setAttribute('subject', 'null')
        sms_el.setAttribute('toa', '0')
        sms_el.setAttribute('sc_toa', '0')
        sms_el.setAttribute('service_center', 'null')
        sms_el.setAttribute('status', '-1')
        sms_el.setAttribute('locked', '0')
       
    def __str__(self):
        return 'SMS(valid=%d, direction=%s, other_party=%s, java_time=%d, read=%d, body=%s)' % \
            (self.valid, self.direction, self.other_party, self.java_time, self.read, self.body)

def main():
    usage = "usage: %prog nokia_smses_in.csv sms_backup_restore_out.xml"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    nok_filename = args[0]
    sbr_filename = args[1]

    with open(nok_filename, 'r') as nok_file:
        dialect = csv.Sniffer().sniff(nok_file.read(1024))
        nok_file.seek(0)
        csv_reader = csv.reader(nok_file, dialect)
        sbr_doc = Document()
        smses_el = sbr_doc.createElement("smses")
        sbr_doc.appendChild(smses_el)
        for csv_row in csv_reader:
            sms = SMS()
            sms.read_from_nok_csv_row(csv_row)
            sms.read = 1
            if not sms.valid:
                continue

            #print sms

            sms_el = sbr_doc.createElement('sms')
            sms.populate_sbr_element(sms_el)
            smses_el.appendChild(sms_el)

        with open(sbr_filename, 'w') as sbr_file:
            sbr_file.write(sbr_doc.toprettyxml())

if __name__ == '__main__':
    main()
