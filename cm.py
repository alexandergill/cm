"""
manages a cad project

Alexander "Gilly" Gill
alexgillygill@gmail.com
https://gilly.tk
"""

import argparse
import glob
import sys
import os

PARTLIST = 'partlist.csv'
FILELIST = 'filelist.csv'

# format for partlist file
PARTNUMBER = 'partnumber'
DESCRIPTION = 'description'
LOCATION = 'par file location'
STATUS = 'status'
PARTLISTFORMAT = [PARTNUMBER, DESCRIPTION, LOCATION, STATUS]

# format for filelist file
FILELISTFORMAT = ['file', PARTNUMBER]

class Part:
    """a single part"""
    partnumber = 'DEADBEEF'
    description = 'uninitialised part'
    location = ''
    status = 'inactive'
    def activate(self):
        """set the part to active"""
        self.status = 'active'
    def deactivate(self):
        """set the part to inactive"""
        self.status = 'inactive'

def openpartlist():
    """opens and returns PARTLIST for reading and writing"""
    # TODO: read file after open and initialise if empty
    if os.path.isfile(PARTLIST):
        return open(PARTLIST, 'a+')
    else:
        # no partlist, so create one
        partlist = open(PARTLIST, 'a+')
        import csv
        writer = csv.writer(partlist)
        writer.writerow(PARTLISTFORMAT)
        return partlist

def exists(partnumber, partlist):
    """checks if a partnumber is in partlist"""
    # move to begining of file so it can all be read
    partlist.seek(0, os.SEEK_SET)

    import csv
    reader = csv.reader(partlist)
    partnumber_loc = PARTLISTFORMAT.index(PARTNUMBER)

    # search entire partlist for partnumber in collumn partnumber_loc
    for entry in reader:
        if entry[partnumber_loc] == partnumber:
            return True

    return False

def add_part(filename, partlist):
    """adds a part to partlist"""
    part = Part()

    part.partnumber = filename
    # check if the part is already in partlist
    if exists(part.partnumber, partlist):
        print('part is already in partlist: ' + part.partnumber)
    else:
        import csv
        writer = csv.writer(partlist)
        # add to end of partlist
        partlist.seek(0, os.SEEK_END)
        writer.writerow([part.partnumber, part.description, part.location,
                         part.status])

def parse_args(args):
    """returns the arguments the user gave"""
    parser = argparse.ArgumentParser(description='manage a cad project')
    parser.add_argument('command', choices=['add', 'remove'],
                        help='the cm command to run')
    parser.add_argument('options', nargs='*',
                        help='options for the command to take')
    args = parser.parse_args(args)
    return args

def add(options):
    """add some files to partlist.csv"""
    parser = argparse.ArgumentParser(description='add a file', prog='cm add')
    parser.add_argument('files', nargs='*', help='the files to add')
    opts = parser.parse_args(options)

    # interate over files in options, and add them to partlist
    with openpartlist() as partlist:
        for filereq in opts.files:
            for filename in glob.glob(filereq, recursive=True):
                add_part(filename, partlist)

def main():
    """execute when not being loaded as a library"""
    args = parse_args(sys.argv[1:])

    if args.command == 'add':
        add(args.options)
    elif args.command == 'remove':
        print('this will remove')
    else:
        raise UserWarning('invalid argument')

if __name__ == "__main__":
    main()
