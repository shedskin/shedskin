#include "serial.hpp"
#include <assert.h>

namespace __serial__ {

#define SERIAL_DEVICE 	"/dev/ttyUSB0"
//#define SERIAL_DEVICE 	"/dev/ttyS0"


int Serial::open()
{
  	fd = ::open(SERIAL_DEVICE, O_RDWR | O_NOCTTY | O_NONBLOCK);
  	assert(fd>=0);

    fcntl(fd, F_SETFL, 0); 

    _reconfigurePort();

    //printf("open %d\n", fd);
}

void Serial::_reconfigurePort() {
    struct termios  tty;
  	tcgetattr(fd, &tty);

    tty.c_cflag |= (CLOCAL|CREAD);
    tty.c_lflag &= ~(ICANON|ECHO|ECHOE|ECHOK|ECHONL|ECHOCTL|ECHOKE|ISIG|IEXTEN);
    tty.c_oflag &= ~(OPOST);
    tty.c_iflag &= ~(INLCR|IGNCR|ICRNL|IGNBRK); //|IUCLC);

    tty.c_cflag &= ~(CSIZE);
    tty.c_cflag |= (CS8);
    tty.c_cflag &= ~(CSTOPB);

    tty.c_iflag &= ~(INPCK|ISTRIP);
    //tty.c_cflag &= ~(PARENB|PARODD);

    tty.c_cflag &= ~(PARODD);
    tty.c_cflag |= (PARENB);

    tty.c_iflag &= ~(IXON|IXOFF); //|IXANY);
    //tty.c_cflag &= ~(CRTSCTS);

    if(baudrate == 9600) {
        cfsetospeed(&tty, B9600);
        cfsetispeed(&tty, B9600);
    }
    else if (baudrate == 38400) {
        cfsetospeed(&tty, B38400);
        cfsetispeed(&tty, B38400);
    }
    else
        assert(0); 

  	tty.c_cc[VMIN]  = 1;
  	tty.c_cc[VTIME] = 1;

  	tcsetattr (fd, TCSANOW, &tty);

}

int Serial::close()
{
  	int result = ::close(fd);
  	assert (result==0);
}

int Serial::setRTS(int on) {   
    int status;

    ioctl(fd, TIOCMGET, &status);

    if(on)
        status |= TIOCM_RTS;
    else
        status &= ~TIOCM_RTS;

    ioctl(fd, TIOCMSET, &status);

    /*int flags = TIOCM_RTS;

    if (on)
        ioctl(fd, TIOCMBIS, &flags);
    else
        ioctl(fd, TIOCMBIC, &flags);*/

}

int Serial::setDTR(int on) {
    int status;

    ioctl(fd, TIOCMGET, &status);

    if(on)
        status |= TIOCM_DTR;
    else
        status &= ~TIOCM_DTR;

    ioctl(fd, TIOCMSET, &status);

    /*int flags = TIOCM_DTR;

    if(on)
        ioctl(fd, TIOCMBIS, &flags);
    else
        ioctl(fd, TIOCMBIC, &flags); */

}

int Serial::setBaudrate(int r) {
    this->baudrate = baudrate;
    _reconfigurePort();
}

int Serial::flushInput() {
    tcflush(fd, TCIFLUSH);
}

int Serial::flushOutput() {
    tcflush(fd, TCOFLUSH);
}

str *Serial::read(int size) {
    str *r = new str();
    unsigned char c;

    for(int i=0; i<size;i++) {
        ::read(fd, &c, 1);
        r->unit += c; 
        //printf("read %d\n", c);  
    }
    return r;   

/*    fd_set rfds;
    int retval;

    if(size > 0) {
        while(len(r) < size) {
            struct timeval tv;
            tv.tv_sec = 1;
            tv.tv_usec = 0;

            FD_ZERO(&rfds);
            FD_SET(fd, &rfds);

            retval = select(1, &rfds, 0, 0, &tv);
            printf("retval %d\n", retval);
            assert(retval!=-1);

            if(retval) {
                retval = read(fd, &c, 1);
                assert(retval==1);
                r->unit += c;
                printf("read %d\n", c); 
            }
            else
                break;
        }
    }    
        
    return r; */
}

int Serial::write(str *data) {
    unsigned char c;
    for(int i=0; i<data->unit.size(); i++) {
        c = data->unit[i];
        int result = ::write(fd, &c, 1);
        assert(result==1);

        //printf("write %d\n", c); 
    }
    flushOutput();
    flushInput();
}

Serial::Serial(str *port, int baudrate, int bytesize, str *parity, int stopbits, int timeout, int xonxoff, int rtscts) {
    this->baudrate = baudrate;
    open();

}


void __init() {

}

} // namespace __serial__
