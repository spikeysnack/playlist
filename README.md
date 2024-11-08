![playlist](https://github.com/spikeysnack/playlist/blob/master/doc/playlist.png)

playlist 

version: 1.8 

status: Release 

build: 25 Aud 2023


Description
===========

	Generate m3u playlists from the command line.

	Works for mp3, flac, m4a, and ogg files.

Requires
========
	python 2.7 or python 3.x
	
	metaflac   (for flac)

	mp3info    (for mp3 )

	mp4ingfo   (for m4a, mp4)

	ogginfo    (for oga, ogg)


##      usage:

             playlist

```bash
             playlist  [option] <dir>

             -a    use <current-dir>.m3u as playlist name

             -c    check system for info utilities

             -f    <file>  write m3u to file instead of standard output

             -h    print this help

             -q    quiet no warnings or info

             -s    sort playlist numerically
  
             -r    recursively descend into directories

             -R    randomize playlist

```

###            playlist outputs a well-formed m3u file
###            from a list of flac, mp3, ogg, or m4a files in a directory.
###            If no directory is given, the current dir is tried.
###            The output is to standard output; however you may
###            direct it to a file with the stream redirect operator (>).

####            Example:

                     playlist dir > myplaylist.m3u    output to file
               
                     playlist -a *.flac             output to <dir>.m3u
	           
                          
	                    

[playlist github](https://github.com/spikeysnack/playlist)


[spikeysnakc@gmail.com](spikeysnack@gmail.com)
