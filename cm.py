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

PARTNUMBER = 'partnumber'
DESCRIPTION = 'description'
PARLOC = 'par file location'
STATUS = 'status'
PATH = 'file'
PARTLISTFORMAT = [PARTNUMBER, DESCRIPTION, PARLOC, STATUS]

FILELISTFORMAT = [PATH, PARTNUMBER]

SOURCEDIR = 'source'
EXTENSIONS = ['.par', '.pdf', '.dft']

class Part:
    """a single part"""
    partnumber = 'DEADBEEF'
    description = 'uninitialised part'
    location = ''
    status = 'active'
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

def openfilelist():
    """opens and returns FILELIST for reading and writing"""
    # TODO: read file after open and initialise if empty
    if os.path.isfile(FILELIST):
        return open(FILELIST, 'a+')
    else:
        # no partlist, so create one
        filelist = open(FILELIST, 'a+')
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
        if entry[column] == string:
            return True

    return False

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

def add_file(path, filelist):
    """adds a file to filelist, adds new part if does not exist"""
    # check if file is already in FILELIST
    if not exists(path, filelist, FILELISTFORMAT.index(PATH)):
        import csv
        writer = csv.writer(filelist)
        # add to end of filelist
        filelist.seek(0, os.SEEK_END)
        writer.writerow([path, 'deadbeef'])

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
                add_file(fileloc, filelist)

def new(options):
    """makes a new part and its part file"""
    pass

def debug():
    partlist = openpartlist()
    part = Part()
    part.partnumber = 'foob'
    part.description = 'bar'
    part.location = 'foo/bar/foob.par'
    part.activate()
    add_part(part, partlist)

def main():
    """execute when not being loaded as a library"""
    print(sys.argv[1:])
    args = parse_args(sys.argv[1:])
    print(args.command)
    print(args.options)
    if args.command == 'add':
        add(args.options)
    elif args.command == 'build':
        print('not yet implemented')
    elif args.command == 'remove':
        print('not yet implemented')
    elif args.command == 'new':
        print('not yet implemented')
    else:
        raise UserWarning('invalid argument: ' + args.command)

if __name__ == "__main__":
    main()
