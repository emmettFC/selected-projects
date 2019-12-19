
import re
from ftplib import FTP

class Parser:
    
    def run_header(self, txt):
        txt = __import__('re').sub('\r', '', txt)
        hd  = txt[txt.find('<ACCESSION-NUMBER>'):txt.find('<DOCUMENT>')]
        hd  = filter(None, hd.split('\n'))
        return self.parse_header(hd)
    
    def parse_header(self, hd):
        curr = {}
        i = 0
        while i < len(hd):
            h = hd[i]
            if re.search('>.+', h) is not None:
                # Don't descend
                key = re.sub('<|(>.*)', '', h)
                val = re.sub('<[^>]*>', '', h)
                curr[key] = [val]
                i = i + 1
            else:
                if re.search('/', h) is None:
                    key = re.sub('<|(>.*)', '', h)
                    end = filter(lambda i:re.search('</' + h[1:], hd[i]), range(i, len(hd)))
                    tmp = curr.get(key, [])
                    if len(end) > 0:
                        curr[key] = tmp + [self.parse_header(hd[(i + 1):(end[0])])]
                        i = end[0]
                    else:
                        curr[key] = tmp + [None]
                        i = i + 1
                else:
                    i = i + 1
        return curr


class Filer:
    
    suffix_of_interest = '.hdr.sgml'
    content            = []
    content_parsed     = []
    parser             = Parser()
    
    def __init__(self, cik, connection):
        self.cik = str(int(cik))
        self.connection = connection
        self._go_to_directory()
    
    def _go_to_directory(self):
        self.connection.cwd('/edgar/data/' + self.cik)
    
    def ls(self):
        return self.connection.dir()
    
    def ls_d(self):
        return self.connection.retrlines('LIST */')
    
    def files_of_interest(self):
        cmd = 'LIST */*/*' + self.suffix_of_interest
        lines = []
        self.connection.retrlines(cmd, lambda x: self._process_foi(x, lines))
        return lines
    
    def _process_foi(self, line, lines):
        lines.append(line.split(' ')[-1])
    
    def download_file(self, path):
        x = []
        self.connection.retrbinary('RETR ' + path, x.append)
        return ''.join(x)
    
    def download_foi(self):
        foi = self.files_of_interest()
        for f in foi:
            print 'downloading ' + f
            self.content.append(self.download_file(f))
        return self.content
    
    def parse_foi(self):
        self.content_parsed = [self.parser.run_header(c) for c in self.content]
        return self.content_parsed


class SECFTP:
    
    parser = Parser()
    
    def __init__(self, connection):
        self.connection = connection
    
    def url_to_path(self, url):
        path = re.sub(r"-|.txt", "", url) + '/' + re.sub('.txt', '.hdr.sgml', url.split("/")[-1])
        return path
    
    def download(self, path):
        x = []
        self.connection.retrbinary('RETR ' + path, x.append)
        return ''.join(x)
    
    def download_parsed(self, path):
        print 'downloading ' + path
        f = self.download(path)
        return self.parser.run_header(f)

