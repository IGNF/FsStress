# FsStress
Stressing File Systems

### Aims
This program aims at evaluating file systems' speed in writing, reading, discovering in different ways. 

### Notice
The program does NOT erase anything. 
The file sizes are all expressed in MB (2^^20 b).
The measures are writtien in one report file (one per execution).

### Required packages
The following packages are required : timeit pandas random rqdm

### The doc
- Run with `python FsStress.py <params>`. See below.
- Getting help : `python FsStress.py help`
- Writing <nbfiles> of <size> MB files into the <dir> (dir is optional : default value is the vurrent working dir) : `python FsStress.py <nbfiles>x<size> <dir>`
- Creating <nbdirs>, and writing <nbfiles> of <size> MB file in each : `python FsStress.py <nbdirs>x<nbfiles>x<size> <dir>`
- Discovering what's in a <dir> : `python FsStress.py discover <dir>`
- Reading all the files in a <dir> : `python FsStress.py read <dir>`
- Randomly reading : ` python FsStress.py rread <delay> <dir>`. This randomly reads 1 MB pieces of the files in <dir>, for a <delay> seconds dureation.
- Randomly write : still to bo done...
