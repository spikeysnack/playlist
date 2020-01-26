#!/usr/bin/env python
# -*- coding: utf-8 -*-

# creates a playlist from a list of flac, mp3, or m4a files
#
# for flac and friends see https://xiph.org/flac/
# replace


""" playlist.py

               creates am M3UEXT playlist from a list of flac, mp3, ogg, or m4a files

"""

#-----------------------------------------
__author__      = "Chris Reid"

__category__    = "audio playlist"

__copyright__   = "Copyright 2018-2020"

__country__     = "United States of America"

__credits__     = ["Python Software Foundation", "Free Software Foundation" ]

__email__       = "spikeysnack@gmail.com"

__file__        = ["playlist.py"]

__license__     = """Free for all non-commercial purposes.
                  Modifications allowed but original attribution must be included.
                  see (http://creativecommons.org/licenses/by-nc/4.0/)"""

__maintainer__  = "chris Reid"

__modification_date__ = "25 Jan 2020"

__version__     = "1.8"

__status__      = "Release"

__URL__         = "https://github.com/spikeysnack/playlist"

__depends__     = ( "metaflac", "mp3info", "mp4info", "ogginfo" )

__extensions__   = ( "flac" , "mp3", "m4a", "ogg" )



# library imports

import os
import sys
import shutil
import glob
import fileinput
import subprocess
import fnmatch
from random import shuffle


# globals
# extensions we can handle


extensions = ( "flac" , "mp3", "m4a", "ogg" )

PY3 = sys.version_info > (3,) #global boolean

album_name_g  = ""  # global
alb_count = 0

artist_name_g = ""
art_count = 0

quiet_g= False

#posix exit codes
NOERR  = 0 # normal exit
EPERM  = 1 # operation not permitted
ENOENT = 2  # no such file or directory
EINVAL = 22 # invalid argument
ENOSYS = 38 # function not implemented


def set_albumname(name=""):
    """ try to set the album name """
    global album_name_g
    global alb_count

    alb_count +=1


    if not album_name_g == "":

        album_name_g = name

    elif name != album_name_g:

        album_name_g="compilation"

    else:
        pass



def set_artistname(name=""):
    """ try to set the album name """

    global artist_name_g

    global art_count

    art_count +=1


    if not artist_name_g:

        artist_name_g = name

    elif name != artist_name_g:

        artist_name_g="Various Artists"

    else:
        pass





# python 2.7 doesn't have shutil.which so we will fake it.
#---------------------
def which(executable):

    """ Check if executable is found in the user's path

        python 2.7 doesn't have shutil.which so we will add one.

    Args:
        executable (string): a file name

   Returns:
        string: the path to the executable or None

    """
    # user has an executable search path
    user_path = os.environ["PATH"].split(":")

    home = os.environ["HOME"]

    # from /etc/environment
    sys_path = [ "/sbin", "/bin",
                 "/usr/sbin", "/usr/bin", "/usr/games",
                 "/usr/local/bin", "/usr/local/sbin" , "/usr/local/games" ]

    # intersection of sets yeilds set without duplicates
    binpath= list(set(sys_path)|set(user_path))

    fullpath = ""

    for path in binpath:

        fullpath = path + "/" + executable

        e = os.path.exists ( fullpath )
        if e:
            break

    if e:
        return fullpath
    else:
        return None

#------------
def info(w=""):
    sys.stdout.write( "INFO: %s\n" % w)

def warning(w=""):
    sys.stderr.write( "WARNING: %s\n" % w)

def fatal(err="", es=1 ):
    sys.stderr.write( "FATAL: %s\n" % err)
    sys.exit(es)


#-----------
def version(stream=sys.stdout):
    """ version message """

    ver = (
        "playlist version:",__version__ ,
        "status:", __status__ ,
        "build:", __modification_date__ )

    msg = " ".join ( ver )

    stream.write("%s\n" % msg)




#-----------
def usage(stream=sys.stdout, len="short"):
    """ usage message """



    shortmsg = \
    r"""
      usage:
             playlist
             playlist  [option] <dir>

             -a    use <current-dir>.m3u as playlist name

             -c    check system for info utilities

             -f    <file>  write m3u to file instead of standard output

             -h    print this help
    
             -q    quiet no warnings or info 

             -r    recursively descend into directories

             -R    randomize playlist

"""

    longmsg = \
            r"""

            playlist outputs a well-formed m3u file
            from a list of flac, mp3, ogg, or m4a files in a directory.
            If no directory is given, the current dir is tried.
            The output is to standard output; however you may
            direct it to a file with the stream redirect operator (>).

            Example:
                     playlist dir > myplaylist.m3u


            Note:  https://github.com/spikeysnack/playlist

    """

    stream.write("%s\n" % shortmsg)
    
    if len == "long":
        stream.write("%s\n" % longmsg)
        version(stream)



#-----------------------------
def get_flac_entry( flacfile):

    """ extract info from a flac file

    Args:
        flacfile(string): name of a flac audio file

    Returns:
        (string): a M3U-EX  entry for the file

    Raises:
       OSError: file access problems
       ValueError: data not in proper format in flac file

"""
    global album_name_g
    global artist_name_g

    mf    = "metaflac"
    sr    = "--show-sample-rate"
    bps   = "--show-bps"
    tots  = "--show-total-samples"
    art   = "--show-tag=artist"
    tit   = "--show-tag=title"
    alb   = "--show-tag=album"

    mfcmd = [ mf, tit, art, alb, sr, tots, flacfile ]

    if not which(mf):
        fatal(" I can't find metaflac in path. Install?]\n", ENOENT)


    flacexists = os.path.exists ( flacfile )

    if not flacexists:
        return None
    else:
        try:
            p = subprocess.Popen( mfcmd , stdout=subprocess.PIPE)

            databytes, err = p.communicate()

            data = databytes.decode('utf-8')

            info = data.split('\n')
            # print(info)

            title  = info[0].split('=')[1]
            artist = info[1].split('=')[1]
            album  = info[2].split('=')[1]
            sample_rate  =  int(info[3])
            total_samples = int(info[4])

            set_artistname(artist)
            set_albumname(album)

        except OSError as oserr:
            if not quiet_g: 
                warning(( str(oserr) ))

        except ValueError as valerr:
            if not quiet_g:
                warning(( str(valerr) ))

        secs= round( total_samples / sample_rate )

        output = "#EXTINF:" + str(secs) + "," + artist + " - " + title + "\n" + flacfile
        # print ("output\t[%s]\n" % output )

        return output


#---------------------------
def get_mp3_entry( mp3file):

    """ extract info from an mp3 file

    Args:
        mp3file(string): name of a mp3 audio file

    Returns:
        (string): a M3U-EX  entry for the file

    Raises:
       OSError: file access problems
       ValueError: data not in proper format in mp3 file


   Note:
       "<file>  does not have an ID3 1.x tag" is an error that comes
        if file has no  ID3v1 tag. It may have and IDv2 tag, though,
        and be perfectly legitimate. Try using a tagging program
        like mp3tag (windows, works with wine on linux) to copy the id3v2
        tag to an id3v1 tag and it will work. or the tags might actually be
        missing. This function tries to get the data from the file name if so.

"""

    # ver = "%v"
    # sr  = "%Q"
    # bps = "%r"
    # frames = "%u"
    # art   = "%a"
    # tit   = "%t"
    # alb   = "%l"
    mp    = "mp3info"

    if not which(mp):
        fatal("I can't find mp3info in path. Install?]\n", ENOENT)


    mp3exists = os.path.exists ( mp3file )

    options = "%a\n%t\n%l\n%S\n"

    output = None

    if not mp3exists:
        return None
    else:
        try:

            p = subprocess.Popen( [mp, "-p", options,  mp3file ] , stdout=subprocess.PIPE)

            infobytes, err = p.communicate()
            info = infobytes.decode('utf-8')
            info =  info.split('\n')

            artist =  info[0]
            title  =  info[1]
            album  =  info[2]
            secs   =  info[3]

            output = "#EXTINF:" + str(secs)  + "," + artist + " - " + title + "\n" + mp3file

            # print("output:\t %s\n" % output )

            set_albumname(album)

            set_artistname(artist)

        except OSError as o:
            print(( str(0) ))

        except ValueError as v:
            print(( str(v) ))

    return output

#---------------------------

def get_m4a_entry( m4afile):

    """ extract info from an m4a (itunes)  file

    Args:
        m4afile(string): name of a m4a audio file

    Returns:
        (string): a M3U-EX  entry for the file

    Raises:
       OSError:    file access problems
       ValueError: data not in proper format in m4a file

"""
# mp4info output:
#
# 01 J.S. Bach - English Suite N.2 Bourree 1.m4a:
# Track	Type	Info
# 1	audio	alac, 102.000 secs, 875 kbps, 44100 Hz
#  Name: J.s. Bach - English Suite N.2: Bourree 1
#  Artist: Eddy Antonini
#  Sort Artist: Eddy Antonini
#  Encoded with: qaac 0.47, QuickTime 7.6.9
#  Release Date: 1998
#  Album: When Water Became Ice
#  Sort Album: When Water Became Ice
#  Track: 1 of 12
#  Genre: Power Metal
#  Cover Art pieces: 1
#  Album Artist: Eddy Antonini
#  Sort Album Artist: Eddy Antonini
#  Lyrics:
#  [instrumental]

    global album_name_g
    mp4info    = "mp4info"
    artist = ""
    title  = ""
    album = ""
    secs   = 0


    if not which(mp4info):
        fatal("[can't find mp4info in path. Install?]\n", ENOENT)


    m4aexists = os.path.exists ( m4afile )

    samples_per_frame = 0
    secs = -1

    if not m4aexists:
        return None
    else:
        try:

            p = subprocess.Popen( [mp4info,  m4afile ] ,
                                  stderr=subprocess.PIPE,
                                  stdout=subprocess.PIPE )

            mp4_infobytes, err = p.communicate()

            info = mp4_infobytes.decode('utf-8')

            m4ainfo = info.split('\n')

            for entry in m4ainfo:

                if "Artist" in entry:
                    artist = entry.split(':')[1].strip()

                if "Name" in entry:
                    n = entry.split(':')
                    if len(n) == 2:
                        title = str(n[1])
                    else:
                        title = str(n)

                if "Title" in entry:
                    title = entry.split(':',1)[1].strip()

                if "Album" in entry:
                    if not "Gapless" in entry:
                        album = entry.split(':',1)[1].strip()
                        set_albumname(album)

                if "secs" in entry.lower():
                    s = entry.split(',')
                    s = s[1].split()[0]
                    secs = int(round(float(s)))

        except OSError as o:
            if not quiet_g:
                warning(( str(o) ))

        except ValueError as v:
            if not quiet_g:
                warning(( str(v) ))

        m3uline = "#EXTINF:" + str(secs)  + "," + artist + " - " + title + "\n" + m4afile
        return m3uline


#---------------------------
def get_ogg_entry( oggfile):

    """ extract info from an m4a (itunes)  file

    Args:
        m4afile(string): name of a m4a audio file

    Returns:
        (string): a M3U-EX  entry for the file

    Raises:
       OSError: file access problems
       ValueError: data not in proper format in mp3 file

"""
    global album_name_g
    ogg = "ogginfo"
    artist = ""
    title  = ""
    album = ""
    secs   = 0

#    title=Custer's Last Stand
#    artist=Rick Wakeman
#    album=Time Machine
#    genre=Rock
#    date=1988
#    tracknumber=01
# Vorbis stream 1:
#    Total data length: 3411006 bytes
#    Playback length: 4m:02.306s
#    Average bitrate: 112.617702 kb/s


    if not which(ogg):
        fatal("[ I can't find ogginfo in path. Install? ]\n", ENOENT )


    m4aexists = os.path.exists ( oggfile )

    samples_per_frame = 0
    secs = -1

    if not m4aexists:
        return None
    else:
        try:

            p = subprocess.Popen( [ogg, oggfile ] , stdout=subprocess.PIPE)

            infobytes, err = p.communicate()

            ogginfo=infobytes.decode('utf-8')

            ogginfo = ogginfo.split('\n')

            #print( ogginfo )

            for entry in ogginfo:
                #print("OGG ENTRY:\t[%s]\n" % entry )

                if not artist:
                    if "artist" in entry:
                        artist = entry.split('=')[1].strip()

                if not title:
                    if "title" in entry:
                        title = entry.split('=')[1].strip()

                if "album" in entry.lower():
                    album = entry.split('=')[1].strip()
                    set_albumname(album)

                # Playback length: 8m:37.106s
                if "Playback length:" in entry:

                    s = entry.split(':')[1:]
                    #print("s:\t%s\n" % s)

                    # not compatabile with python3
                    #minutes = filter(lambda x: x.isdigit(), s[0])
                    #seconds = filter(lambda x: x.isdigit(), s[1])

                    # python 2 and python3 syntax strip non digits
                    # note: kills decimal point too.
                    minutes = ''.join([x for x in s[0] if x.isdigit()])
                    seconds = ''.join([x for x in s[1] if x.isdigit()])

                   # print("minutes:\t%s\n" % minutes)
                   # print("seconds:\t%s\n" % seconds)

                    secs = (60 * int(minutes)) + (int(seconds)/1000)
                    #print( "SECS:\t[%s]\n" % secs)

        except OSError as o:
            if not quiet_g:
                warning(( str(0) ))

        except ValueError as v:
            if not quiet_g:
                warning(( str(v) ))

        output = "#EXTINF:" + str(secs)  + "," + artist + " - " + title + "\n" + oggfile
        #print("output:\t %s\n" % output )

        return output



#---------------------
def hms(sec):
    """ convert seconds to hms string """

    dhour = int(sec / 3600)
    dmin = int( (sec/60) - dhour*60 )
    dsec = sec - ( dhour*3600 + dmin*60)
    # print ("dhour", dhour)
    # print ("dmin", dmin)
    # print ("dsec", dsec)

    h = "{:02d}".format(dhour)
    m = "{:02d}".format(dmin)
    s = "{:02d}".format(dsec)

    return  ':'.join( (h, m, s) )


#----------------------

def write_m3u( flist , outfile=None , rand=False ):

    """ write out the M3U-EX info  from the mp3 files

    Args:
       flist (string): a list of filenames (mp3 or flac)

    Returns:
        None

    """
    global album_name_g

    duration = 0

    def dur(sec):

        sec  = sec.replace(',', ':')
        #print("sec", sec)
        dur = sec.split(":")
        #print("DUR:", dur)

        if (PY3):
            dur[1]  = round ( float(dur[1]), 0 )

        return int(dur[1])


    out = ""

    # redirect stdout to file.
    # this is for compatibility between python 2 and 3
    if outfile:
        try:
            f = open(outfile, 'w')
            sys.stdout = f
        except IOError as io:

            fatal( "[error opening %s for writing: %s]\n" % (outfile , io), io.errno)

    print ("#EXTM3U\n")


    if rand:
        print ("# SHUFFLED LIST")
        shuffle(flist)

    for entry in flist:

        if ".flac" in entry:
            out = get_flac_entry( entry )

        elif  ".mp3" in entry:
            out = get_mp3_entry( entry )

        elif  ".m4a" in entry:
            out = get_m4a_entry( entry )

        elif  ".ogg" in entry:
            out = get_ogg_entry( entry )

        else:
            continue

        if out:
            duration += dur(out)

            #print("duration::" , duration)


        print( out )

    print(("# Artist: " + artist_name_g) )
    print(("# Album: " + album_name_g)   )

    print(( "# Duration: " + hms(duration) ))

    print ("# playlist.py copyright 2015-2020 by chris reid")



    print("#END\n")

    sys.stdout = sys.__stdout__ # restore stdout
#------------------------------------------

def program_check(programs=None):

    """ see what programs are present to use """
    for p in programs:

        found = which(p)

        if  found:
            print( ("%s: found %s\n" % (p, found)) )
        else:
            if not quiet_g:
                warning( ("%s %s\n" % (p, "not found in path. Install?")) )


#------------------------------------------
def parse_args(args, recursive=False, outfile=None, randomlist=False):

    """ parse the command line arguments

    a low-budget command line option parser.

    Args:
       args (list):         the command line given

    Returns:
       args(list):          the parsed command line
       recursive(boolean):  recurse directories

    """

    global quiet_g

    if len(args) == 0:
        return args, False

    #    for o in args:
    if len(args) > 1:
        o = args[1]
        #  print("o %s\n" % o)

        if len(args) >2:
            if args[2].startswith( '-', 0, 1 ):
                
                fatal( "Only one option can be used.\n")
                usage(sys.stdout)
                sys.exit(22) # EINVAL

        if o in ( "-h", "-help", "--help", "help", "--options" , "options" ):
            usage(sys.stdout, "long")
            sys.exit(NOERR)

        elif o in ( "-v", "-ver", "--version", "version" ):
            version(sys.stdout)
            sys.exit(NOERR)

        elif o in ( "-q", "-quiet", "--quiet", "quiet" ):
            quiet_g = True

        elif o in ( "-a", "-auto", "--auto", "auto" ):

            dirname = os.path.basename( os.getcwd() )
            outfile= ''.join( ( dirname, '.m3u' ) )
            if not quiet_g: info((outfile))

        elif o  in (  "-c", "-check", "--check", "check") :
            programs = [ 'metaflac' , 'mp3info', 'ogginfo' , 'mp4info' ]
            program_check(programs)
            sys.exit(NOERR)

        elif o in ( "-f", "--file" ):

            if len(args) > 2:
                outfile = args[2]
                print(( "playlist: ", outfile))
            else:
                fatal( ("need filename for option  %s\n" % o), EINVAL )

            fpath= os.path.join( os.getcwd() , outfile )

            # print(("fpath:", fpath))

            if os.path.isfile( fpath):
                oldfile = outfile + ".old"
                os.rename(outfile, oldfile)

        elif o in ( "-q", "-quiet", "--quiet", "quiet" ):
            quiet_g= True


        elif o in ( "-r", "--recursive" ):
            recursive = True


        elif o in ( "-R", "--random" ):
            randomlist = True


        elif o in ( "-"):
            fatal(("unkown option %s\n" % o), EINVAL )

        elif o in ( "--"):
            pass

        else:
            usage(sys.stdout)
            fatal( ("unkown option %s\n" % o), EINVAL )


        args.remove(o)


    return (args, recursive, outfile, randomlist)

#------------------------------------------------------------

def get_files(_dir, recursive = False):

    """ get a directory list of wanted files

    Args:
          _dir(list or str):   a string of a filename, dir, or list of
                               files or directories or a mix of both.
         recursive(boolean):  descend into subdirs if true

    Returns:
           audiofiles(list): a list of known audiofiles to process.
                             The strings are the relative path of each file.

    """


    audiofiles=[]

    if isinstance(_dir, str): _dir = [_dir]

    # print ( "_dir:\t%s" % _dir)
    # print ( "recursive:\t%s" % recursive)


    for d in _dir:
        if os.path.isdir(d):
#            print("d:\t%s\n" % d)
            if recursive:
                for root, dirs, files in os.walk(d):
                    for filename in files:
                        if filename.endswith(extensions):
                            audiofiles.append(os.path.join(root, filename ) )

            else:
                if not d.endswith('/'): d = d + "/"
                flist = glob.glob(d+'*')

                for f in flist:
#                    print("GLOB:  %s\n" % f)
                    if  os.path.isdir(f):
                        continue  # skip -- not recursive
                    if f.endswith(extensions):
                        audiofiles.append(f);


        elif os.path.isfile(d):
            if d.endswith(extensions):
                audiofiles.append(d)
        else:
            pass

#    print( "audiofiles: %s\n" % audiofiles)

    return audiofiles

#-----------------------------------------------------------
def main(args):

    """ main driver playlist.py

    Args:
        sys.argv  (list) (string):  command line args

    Returns:
        None

    """

    all_file_list = []
    file_list     = []
    recursive     = False
    randomlist    = False
    outfile       = None

    d             = "."

    args, recursive, outfile, randomlist = parse_args(args, recursive)

    n_args = len(args)


    if n_args == 1:
        d = os.listdir(".")      # use cwd if not given
    elif n_args == 2:
        d = args[1] # file
    else:
        d = args[1:] # list


    all_file_list = get_files( d , recursive)
#    print (all_file_list)

    # check extensions
    if all_file_list:
        for f in all_file_list:
            if '.' in f:
                ext = f.rsplit('.', 1)[1]
                if ext in extensions:
                    file_list.append(f)

    if file_list:
        write_m3u(file_list, outfile, randomlist)
    else:
        # ok options analyzed, lets make some file lists.

        d = os.getcwd() # no file list use current dir
        if not d.endswith('/'): d = d+ "/"

        flacfiles = glob.glob(d + "*.flac")
        mp3files  = glob.glob(d + "*.mp3" )
        oggfiles  = glob.glob(d + "*.ogg" )
        m4afiles  = glob.glob(d + "*.m4a" )

        mp3files = sorted ( mp3files )

        if randomlist:
            shuffle(flacfiles)
            shuffle(fmp3files)
            shuffle(oggfiles)
            shuffle(m4afiles)


        allfiles = flacfiles + mp3files + oggfiles + m4afiles


#        print( "allfiles %s\n" % allfiles)

        if allfiles:
            if randomlist:
                shuffle(allfiles)

            write_m3u( allfiles, outfile )

        elif flacfiles:
            write_m3u( flacfiles, outfile )

        elif mp3files:
            write_m3u( mp3files , outfile)

        elif oggfiles:
            write_m3u( oggfiles ,outfile)

        elif m4afiles:
            write_m3u( m4afiles, outfile )

        else:
            if not quiet_g:
                usage()
                info("no audio files found   (dir?)")
            pass



# program starts here
if ( __name__ == '__main__' ) or (__name__ == '__builtin__'):

   main(sys.argv) # main driver

   sys.exit(NOERR) # clean exit
   
else:
  # something is wrong if we are here
  fatal(("name: " + __name__), ENOSYS)




# Local Variables: #
# mode: python     #
# tab-width: 4     #
# End:             #
