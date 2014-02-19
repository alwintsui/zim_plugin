#!/usr/bin/python

import sys
"""
Custom Tools of zim-wiki: reduce_blanks.py %f
To reduce all continous blank lines into only a blank line in a zim-page file
By Alwin Tsui <alwintsui@gmail.com>
"""
def reduce_zim_page(infile):
    lfile = open(infile, 'r')
    ostr = ""
    lastbk = False
    for line in lfile:
        if line.isspace():
           if lastbk:
	      continue
           else:
              lastbk=True
        else:
           lastbk= False
        ostr += line
    lfile.close()
    ofile = open(infile, 'w')
    ofile.write(ostr)
    ofile.close()

if __name__ == '__main__':
    infile = sys.argv[1] # first commandline argument %f
    reduce_zim_page(infile)

