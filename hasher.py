import hashlib, os

class FileHasher:
    ## Some function that gets the path to the share folder
    ## shareDir = shareDir()
    ##
    ## until then i'm hard coding it for testing

    def __init__(self, path):
        self.shareDir = path
        #**************************************************************
        # Now we generate some useful lists and dictionaries.
        # Note -- HashToFileDict takes quite a while when the share directory has a lot of files
        # or is very large. I hope one of us can fix this by storing this information so that the program
        # can add to or delete entries to this dictionary as needed rather than generating it each time the program
        # starts.
        #

        self.MasterFileList = [x for x in self.getFilesBelow(self.shareDir)] #list of all files in share directory by path

        self.MasterDirList = [x for x in self.getDirsBelow(self.shareDir)] #list of all dirs in share directory by path

        self.HashToFileDict = {self.hashFile(x) : x for x in self.MasterFileList} # { hash: path .. }

        self.FileToHashDict = {v : k for (k,v) in self.HashToFileDict.iteritems()} # { path: hash .. }


    #***********************************************************
    # getDirsBelow(directory) takes a path to a directory and returns a list of
    # paths to subdirectories below the top directory.

    def getDirsBelow(self, directory):
        dirList = []
        for (path, dirs, files) in os.walk(directory):
            for d in dirs:
                dirList.append(os.path.join(path,d))
        return dirList

    #************************************************************
    # getFilesBelow(directory) takes a path to a directory and returns a list of
    # paths to files below that directory. By below we mean it is either in the directory
    # or you can get to it by opening subdirectories.

    def getFilesBelow(self, directory):
        fileList = []
        for (path, dirs, files) in os.walk(directory):
            for f in files:
                fileList.append(os.path.join(path,f))
        return fileList

    #*************************************************************
    # hashFile(pathtofile) takes a 'path/to/file' and returns the sha1sum hash
    # the output is the same as sha1sum < path/to/file

    def hashFile(self, pathtofile):
        SHA1hash = hashlib.sha1()
        f = open(pathtofile, 'rb')
        while True:
            chunk = f.read(1048576) #reads in 1 mb at a time to avoid using up ram on large files.
            if not chunk: break
            SHA1hash.update(chunk)
        f.close()
        return SHA1hash.hexdigest()

    #***************************************************************
    # hashDir(pathtodir) takes a 'path/to/dir' and returns a unique hash for the dir
    # It creates the hash by creating a sorted list of the hashes for every file below the directory
    # and then hashing this list of hashes.

    def hashDir(self, pathtodir):
        SHA1hash = hashlib.sha1()
        HashList = []
        fb = self.getFilesBelow(pathtodir) # generates a list of all the files below the dir
        for f in fb:
            HashList.append(self.FileToHashDict[f]) # this gets the hash for file 'f' and adds it to the list
            HashList.sort() # This sorts the list so that the hash of the HashList will be unique. Right?
        for h in HashList:
            SHA1hash.update(h)
        return SHA1hash.hexdigest()

    #*************************************************
    # HashToPathDict() takes no arguments. It generates the hash: path associations
    # for every file and every dir in the share directory
    #

    def HashToPathDict(self):
        for d in self.MasterDirList:
            self.HashToFileDict[self.hashDir(d)] = d
        return self.HashToFileDict

#    dictOfHashes = HashToPathDict() #So that dictOfHashes is available for use.
