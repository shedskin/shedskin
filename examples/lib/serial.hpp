#ifndef __SERIAL_HPP
#define __SERIAL_HPP

#include "builtin.hpp"

#include <cstdio>
#include <termios.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <time.h>

using namespace __shedskin__;

namespace __serial__ {

class Serial : public pyobj {
public:
    int fd, baudrate;

    Serial(str *port, int baudrate, int bytesize, str *parity, int stopbits, int timeout, int xonxoff, int rtscts);

    int open();
    str *read(int n);
    int write(str *s);
    int close();

    int setRTS(int n);
    int setDTR(int n);
    int setBaudrate(int n);

    int flushInput();
    int flushOutput();

    void _reconfigurePort();

};


void __init();

} // namespace __serial__
#endif
