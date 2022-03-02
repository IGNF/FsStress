## Fox's filesystem stressing
## This program aims at testing the I/O performance
## of different file systems (HD, SSD, etc.)

import sys
import os
import datetime
import timeit
import pandas
import random
import tqdm

## A one Mo array
aMB = bytearray(1024 * 1024)
theResults = []

## The files and dirs, and total number of bytes written, read or discovered
theFilesAndDirs = {"dirs":[],"files":[], "totalBytes":0}

def fPreciseTimeString():
    return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S--%f")

## When the program begins : needed for the report file's name.
theBegin = fPreciseTimeString()

## Compute the name of the file to be written immediately after the call.
def fGetFileName():
    return fPreciseTimeString()+".bin"

## Save the results into a cvs file.
def report(stressPath, action):
    df = pandas.DataFrame (theResults, columns=['Task','Duration'])
    df.to_csv (stressPath+"/"+"stressReport" + action + "-" + theBegin+".csv", sep=";")
    print (df)

## Writes a file fName of size nMo in Mo
def writeFileMo (dirName, nMo):
    filePath = dirName + "/" + fGetFileName()
    f = open (filePath,"wb")
    for i in range (nMo):
        f.write (aMB)

def runHelp():
    print ("fsstress.py : stressing i/o. Unit is 1 MB")
    print ("fsstress.py help : shows this help")
    print ("fsstress.py write <params> <dir> : stresses writes")
    print ("fsstress.py discover <dir> : lists all files")
    print ("fsstress.py read <dir> : discover and read all files")
    print ("fsstress.py rread <delay> <dir>: discover and randomly read pieces of files for <delay> seconds")
    print ("   <params> : <nbfiles>x<size> or")
    print ("   <params> : <nbdirs>x<nbfiles>x<size>")
    return 0

## Stress : writing nbFiles of size nMo MB on dirName
def runStressWrite(dirName, nbFiles, nMo):
    for i in range(nbFiles):
        t=timeit.Timer (lambda: writeFileMo(dirName, nMo))
        duration = t.timeit(number=1)
        print ("time elapsed : ", duration, "s.")
        task="Write-"+str(nMo)+"MB"
        theResults.append ([task, duration])
    report(dirName, "write")

def fParseDirNbNb(s):
    a = s.split("x")
    count = len(a)
    res = [ 0, 0, 0]
    nMo = int (a [count-1])    
    res[2] = nMo
    if (count > 1):
        nF = int (a [count-2])
        res[1] = nF
    if (count > 2):
        nDir = int (a [count-3])
        res[0] = nDir
    return res


def listFilesAndDirs(path):
     l = os.listdir(path)
     for f in l:
        lpath = os.path.join(path, f)
        if os.path.isfile (lpath):
            fSize = os.path.getsize(lpath)
            theFilesAndDirs["files"].append ({"name": lpath, "size":fSize})
            theFilesAndDirs["totalBytes"] += fSize
        elif os.path.isdir (lpath): 
            theFilesAndDirs["dirs"].append (lpath)
            listFilesAndDirs (lpath)

def discover (p):
    t=timeit.Timer (lambda: listFilesAndDirs(p))
    duration = t.timeit(number=1)
    ## print (theFilesAndDirs)
    print ("Discover results :")
    print ("Dirs discovered  :", len(theFilesAndDirs["dirs"]))
    print ("Files discovered :", len(theFilesAndDirs["files"]))
    print ("Duration         :", duration)
    return 0

def readFile (fPath):
    if not os.path.isfile (fPath):
        raise "In readFile ("+ fPAth + ") : not a file."
    fileSize = os.path.getsize(fPath)
    f=open (fPath, "rb")
    bytes = f.read(1024*1024)
    while bytes:
        bytes = f.read(1024*1024)

def readAll(p, verbose = True):
    discover(p)
    nb = len(theFilesAndDirs["files"])
    print ("Start reading : ", nb, "files.")
    print ("Total bytes   : ", theFilesAndDirs["totalBytes"])
    tbRead = 0
    for f in theFilesAndDirs["files"]:
        lpath = f["name"]
        if verbose:
            print ("Reading", lpath, "...", end='')
        t=timeit.Timer (lambda: readFile (lpath))
        duration = t.timeit(number=1)
        tbRead += f["size"]
        if verbose:
            print ("duration :", duration, "s.")
        theResults.append ([lpath, duration])
    report(p, "read")
    print ("Total bytes read :", tbRead)

## Read a file (and measure duration)
def read(p):
    t=timeit.Timer (lambda: readAll(p))
    duration = t.timeit(number=1)
    print ("Read all results :")
    print ("Files read       :", len (theFilesAndDirs["files"]))
    print ("Duration         :", duration)

## Randomly reads a little piece of a file (of size howMuch bytes)
def rreadFile (path, howMuch = 1024):
    fsize = os.path.getsize(path)
    f = open(path,"rb")
    if fsize > howMuch:
        pos = random.randint(0, fsize-howMuch)
        f.seek(pos)
        f.read(howMuch)
    else:
        f.read(fsize)

## Reads randomly 1 Ko in a randomly chosen file.
## Assumes the folder has been discovered.
def rreadN(n):
    rnd = random.Random()
    lFiles = random.choices(theFilesAndDirs["files"], k = n)
    for f in lFiles: 
        rreadFile (f["name"])



theResRRead = { "reads":0, "duration":0.0}

## Randomly read.
def rread(p, delay):
    print ("Discovering ...", end='')
    discover(p)
    startTime = datetime.datetime.now()

    print ("Starting ...")
    nbReads = 100

    pbar = tqdm.tqdm (total = delay)
    update = 0
    while True:
        t=timeit.Timer (lambda: rreadN(nbReads))
        duration = t.timeit(number=1)
        theResRRead["reads"] += nbReads
        theResRRead["duration"] += duration
        currentTime = datetime.datetime.now()
        td = currentTime - startTime
        if td.seconds > update: 
            cran = td.seconds - update
            ## update = td.seconds
            pbar.update (cran)
        
        ### print ("Elapsed : ", td)
        if (td.seconds >= delay):
            break

    print (theResRRead)

## Retrieving the path to be stressed at [position] in [args].
## Returns current directroy if missing.
def tryParsePath (a, position):
    if len(a) > position:
        d = a[position]
        if os.path.isdir(d):
            return d
        print ("!! WARNING : Path " + a + " unknown or not a directory. Back to current working dir")
    ## Not enough parameters : assuming working dir.
    return os.getcwd()        

def main():
    global stressPath
    print ("Launching     : fstress.py")
    print ("Please notice : this program does not erase anything.")
    print ("Now           :", fPreciseTimeString())
    args = sys.argv[1:]
    count=len(args)

    if count == 0:
        return runHelp()
    
    theCommand = args[0]
    print ("Command       :", theCommand)

    if theCommand == "help":
        return runHelp()
    elif theCommand == "write":
        sParams = args[1]
        params = fParseDirNbNb (sParams)
        sPath = tryParsePath (args, 2)
        return runStressWrite (sPath, params[1], params[2])
        return 0
    elif theCommand == "discover":
        return discover(tryParsePath (args, 1))
    elif theCommand == "read":
        return readAll (tryParsePath (args, 1))
    elif theCommand == "rread":
        d = args[1]
        ## if not isdigit(d):
        ##    print ("!! ERROR : Delay is not a number")
        ##    return 1
        nd = int(d)
        print ("Delay : ", nd, "s.")
        p = tryParsePath(args, 2)
        return rread (p, nd)
    
    print ("Command " + theCommand + "unknown")
    return 1

if __name__ == '__main__':
    sys.exit(main())