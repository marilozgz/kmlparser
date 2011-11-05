#!/usr/bin/env python
# encoding: utf-8
"""

kmlparser.py

Created by John Wesonga on 2011-11-03.

"""

import os
import csv
import getpass
from optparse import OptionParser

from BeautifulSoup import BeautifulSoup
import gdata.docs.service
import gdata.docs.data


class KmlParser(object):
    """
        KmlParser
    """ 
    def __init__(self, kmlfile, csvfile):
        self.kmlfile = kmlfile
        self.csvfile = csvfile
        self.outputdata = []
    
    def parse_kml(self): 
        """
            parse_kml
        """
        try:
            handler = open(self.kmlfile).read()
            soup = BeautifulSoup(handler)
            for message in soup.findAll('placemark'):
                locationdata = {}
                coordinates = message.find('coordinates')
                locationdata['geometry'] = '<LineString> %s </LineString>' % (coordinates)
                names = message.findAll('name')
                for name in names:
                    text = name.find(text = True)
                    locationdata['name'] = text
            self.outputdata.append(locationdata)                    
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)

    def write_csv(self):
        """
            write_csv        
        """ 
        outputfile = os.getcwd() + '/' + self.csvfile
        try:
            out = open(outputfile,'w')
            print 'Writing output to file ' + str(outputfile)
            try:
                fieldnames = sorted(self.outputdata[0].keys())
                writer = csv.DictWriter(out, dialect = 'excel', 
                        fieldnames = fieldnames, 
                        extrasaction='ignore', quoting=csv.QUOTE_NONNUMERIC)
                headers = dict((n, n) for n in fieldnames)
                writer.writerow(headers)
                for row in self.outputdata:
                    writer.writerow(row)
            finally:
                out.close()
        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
        return outputfile


    def upload(self, output_file):
        """
            upload      
        """
        email = raw_input('Please enter your gmail address: ')
        password = getpass.getpass('Please enter your gmail password: ')
        client = gdata.docs.service.DocsService()
        client.ClientLogin(email, password, 'kmltocsv')
        uploaded_filename = self.csvfile[0:-4]
        mediasource = gdata.data.MediaSource(file_path = output_file,
             content_type = gdata.docs.service.SUPPORTED_FILETYPES['TXT'])
        entry = client.Upload(mediasource, uploaded_filename)
        if entry:
            print 'Upload successful '
            print 'Document now accessible at:', entry.GetAlternateLink().href
        else:
            print 'Upload error'

def main():
    """
        Main method
    """
    parser = OptionParser()
    parser.add_option("-f", "--file", dest = "kmlfile", 
                    help = "KML file to be parsed", 
                    metavar = "FILE")                     
    parser.add_option("-d", "--output", dest = "csvfile", 
                   help = "CSV output file", 
                   metavar = "FILE")
    (options, args) = parser.parse_args()
    if not options.kmlfile:
        print "please type python " \
              "kmlparser.py --file=[kmlfilename] --output=[csvfilename]"     
    elif not options.csvfile:
        print "please type python " \
              "kmlparser.py --file=[kmlfilename] --output=[csvfilename]"
    else:
        kmlparser = KmlParser(kmlfile=options.kmlfile, 
                             csvfile=options.csvfile)               
        kmlparser.parse_kml()
        upload_file = kmlparser.write_csv()
        kmlparser.upload(upload_file)
if __name__ == "__main__":
    main()




 