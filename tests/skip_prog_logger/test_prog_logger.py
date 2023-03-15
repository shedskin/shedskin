# from: https://pythontic.com/modules/select/select

import select
import os
import os.path

# Class representing a log file
class LogFile:
    def __init__(self, logFileName, logFile, descriptor):
        self.myLogFileName = logFileName
        self.myLogFile = logFile
        self.myDescriptor = descriptor


def test_logger():
    if os.path.exists("testdata"):
        testdata = "testdata"
    elif os.path.exists("../testdata"):
        testdata = "../testdata"
    else:
        testdata = "../../testdata"

    # List of log files
    logFiles = []

    logfile1 = os.path.join(testdata, "LogFile1.txt")
    file1 = open(logfile1, "w")
    logFile1 = LogFile(logfile1, file1, file1.fileno())
    logFiles.append(logFile1)

    logfile2 = os.path.join(testdata, "LogFile2.txt")
    file2 = open(logfile2, "w")
    logFile2 = LogFile(logfile2, file2, file2.fileno())
    logFiles.append(logFile2)

    logfile3 = os.path.join(testdata, "LogFile3.txt")
    file3 = open(logfile3, "w")
    logFile3 = LogFile(logfile3, file3, file3.fileno())
    logFiles.append(logFile3)

    # List of descriptors for read, write and exception conditions
    rdescriptors = []
    wdescriptors = []
    xdescriptors = []

    # Add the write descriptors to the write descriptor list
    for log in logFiles:
        wdescriptors.append(log.myDescriptor)

    # Wait for write condition
    rlist, wlist, xlist = select.select(rdescriptors, wdescriptors, xdescriptors)

    # print("Number of descriptors ready for write %d" % (len(wlist)))
    assert len(wlist) == 3

    # Write to all the logs that are ready
    for writeDescriptor in wlist:
        for log in logFiles:
            if log.myDescriptor is writeDescriptor:
                log.myLogFile.write("Starting to log events")

    for f in logFiles:
        assert os.path.exists(f.myLogFileName)
        f.myLogFile.close()
        os.remove(f.myLogFileName)


def test_all():
    test_logger()


if __name__ == "__main__":
    test_all()
