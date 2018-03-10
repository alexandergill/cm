"""
manages a cad project

Alexander "Gilly" Gill
alexgillygill@gmail.com
https://gilly.tk
"""

import sys

if sys.version_info[0] < 3:
    raise Exception('cm needs python 3 or later.')

import argparse
import glob
import os

PARTLIST = 'partlist.csv'
FILELIST = 'filelist.csv'

PARTNUMBER = 'partnumber'
DESCRIPTION = 'description'
PARLOC = 'par file location'
STATUS = 'status'
PATH = 'file'
PARTLISTFORMAT = [PARTNUMBER, DESCRIPTION, PARLOC, STATUS]

FILELISTFORMAT = [PATH, PARTNUMBER]

SOURCEDIR = 'source'
EXTENSIONS = ['.par', '.pdf', '.dft']

NEWPASTA = 'overwrite this file with a part file'

class Part:
    """a single part"""
    def __init__(self):
        self.partnumber = ''
        self.description = 'uninitialised part'
        self.location = ''
        self.status = 'active'
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
        return open(PARTLIST, 'a+', newline='')
    else:
        # no partlist, so create one
        partlist = open(PARTLIST, 'a+', newline='')
        import csv
        writer = csv.writer(partlist)
        writer.writerow(PARTLISTFORMAT)
        return partlist

def openfilelist():
    """opens and returns FILELIST for reading and writing"""
    # TODO: read file after open and initialise if empty
    if os.path.isfile(FILELIST):
        return open(FILELIST, 'a+', newline='')
    else:
        # no partlist, so create one
        filelist = open(FILELIST, 'a+', newline='')
        import csv
        writer = csv.writer(filelist)
        writer.writerow(FILELISTFORMAT)
        return filelist

def exists(string, csvfile, column):
    """returns whether string is in column of csvfile"""
    # move to begining of file so it can all be read
    csvfile.seek(0, os.SEEK_SET)

    import csv
    reader = csv.reader(csvfile)

    # search entire partlist for partnumber in collumn partnumber_loc
    for entry in reader:
        try:
            if entry[column] == string:
                return True
        except IndexError: # column is not in this row. ignore
            pass

    return False

def get_new_partnumber(partlist):
    """creates a new partnumber unique to partlist"""
    from random import randrange
    col = PARTLISTFORMAT.index(PARTNUMBER)
    # try 60,000 times to get a new partnumber
    for _ in range(0, 60000):
        new_partnumber = format(randrange(0xffff), '04x')
        if not exists(new_partnumber, partlist, col):
            return new_partnumber
    # couldn't find a unique one
    raise Exception("couldn't find a new unique partnumber")
    #TODO: handle this properly

def get_active_parts(partlist):
    # move to begining so all of partlist can be read
    partlist.seek(0, os.SEEK_SET)

    import csv
    reader = csv.reader(partlist)

    # search in STATUS column for 'active'
    status_column = PARTLISTFORMAT.index(STATUS)
    partnumber_column = PARTLISTFORMAT.index(PARTNUMBER)
    for entry in reader:
        try:
            if entry[status_column] == 'active':
                yield entry[partnumber_column]
        except IndexError: # status_column is not in this row. ignore
            pass

def get_file_locations_by_partnumber(partnumber, filelist):
    raise Exception('not yet implemented')

def add_part(part, partlist):
    """adds a part to partlist"""

    # check if the part is already in partlist
    if exists(part.partnumber, partlist, PARTLISTFORMAT.index(PARTNUMBER)):
        print('part is already in partlist: ' + part.partnumber)
    else:
        import csv
        writer = csv.writer(partlist)
        # add to end of partlist
        partlist.seek(0, os.SEEK_END)
        writer.writerow([part.partnumber, part.description, part.location,
                         part.status])

def add_file(path, partnumber, filelist):
    """adds a file to filelist"""
    # check if file is already in FILELIST
    if not exists(path, filelist, FILELISTFORMAT.index(PATH)):
        import csv
        writer = csv.writer(filelist)
        # add to end of filelist
        filelist.seek(0, os.SEEK_END)
        writer.writerow([path, partnumber])
    else: print('file is already in filelist: ' + path)

def parse_args(args):
    """returns the arguments the user gave"""
    parser = argparse.ArgumentParser(description='manage a cad project')
    parser.add_argument('command', choices=['add'],
                        help='the cm command to run')
    parser.add_argument('options', nargs='*',
                        help='options for the command to take')
    args = parser.parse_args(args)
    return args

def add(options):
    """add some files to filelist.csv"""
    parser = argparse.ArgumentParser(description='add a file', prog='cm add')
    parser.add_argument('files', nargs='*', help='the files to add')
    opts = parser.parse_args(options)

    # interate over files in options, and add them to filelist
    with openpartlist() as partlist, openfilelist() as filelist:
        for filereq in opts.files:

            if os.path.isdir(filereq):
                locations = glob.glob(filereq + '/**', recursive=True)
            else:
                locations = glob.glob('**/' + filereq, recursive=True)

            for fileloc in locations:
                # do nothing if the file isn't in SOURCEDIR
                if os.path.normpath(fileloc).split(os.sep)[0] != SOURCEDIR:
                    continue

                # do nothing if the file is not of allowed type
                if os.path.splitext(fileloc)[1] not in EXTENSIONS:
                    continue

                #get partnumber
                print("which part does this file belong to: "
                      + os.path.basename(fileloc))
                partnumber = input('partnumber: ')

                # if partnumber does not exist, make a new part and add it to
                # partlist
                if not exists(partnumber, partlist,
                              PARTLISTFORMAT.index(PARTNUMBER)):
                    part = Part()
                    part.partnumber = partnumber

                    # if this is the par file, add it as location
                    if os.path.splitext(fileloc)[1] == '.par':
                        part.location = fileloc
                    else:
                        part.location = 'err: no par location'

                    # get a description for the part
                    print('give this part a description')
                    part.description = input('eg. "Drive Shaft" > ')

                    add_part(part, partlist)
                #add file to filelist
                add_file(fileloc, part.partnumber, filelist)

def new(options):
    parser = argparse.ArgumentParser(description='make a new managed part',
                                     prog='cm new')
    parser.add_argument('-d', '--description', required=True,
                        help='a description of the new part')
    parser.add_argument('-p', '--partnumber',
                        help='optionally give it a partnumber')
    parser.add_argument('-l', '--location', default=SOURCEDIR,
                        help='optionally define a location for the part')
    opts = parser.parse_args(options)

    partlist = openpartlist()

    part = Part()
    part.description = opts.description
    if opts.partnumber != None:
        part.partnumber = opts.partnumber
    else:
        part.partnumber = get_new_partnumber(partlist)

    # strip punctuation and make a standard filename
    import re
    filename = (re.sub(r'[^\w\s]','',part.description).lower().replace(' ','-')
               + '-' + part.partnumber)
    part.location = os.path.join(opts.location, filename) + EXTENSIONS[0]

    # save a new file to the location
    def safe_open_write(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return open(path, 'x')
        
    try:
        with safe_open_write(part.location) as newfile:
            newfile.write(NEWPASTA)
            print('saved a new file to ' + part.location)
            print(NEWPASTA)
            add_part(part, openpartlist())
            add_file(part.location, part.partnumber, openfilelist())
    except FileExistsError:
        print('file {0} already exists in that location'.format(filename))

def build(options):
    """puts all active files into /build and generates bill of materials"""
    with openpartlist() as partlist, openfilelist() as filelist:
        for part in get_active_parts(partlist):
            for source_loc in get_file_locations_by_partnumber(part.partnumber, filelist):
                pass

def main():
    """execute when not being loaded as a library"""
    try:
        command = sys.argv[1]
        if command == 'add':
            add(sys.argv[2:])
        elif command == 'build':
            print('not yet implemented')
        elif command == 'remove':
            print('not yet implemented')
        elif command == 'new':
            new(sys.argv[2:])
        else:
            raise UserWarning('no such argument')
    except (IndexError, UserWarning):
        print('usage: cm <command> <options>\nread documentation for details\n')
        raise

if __name__ == "__main__":
    main()
