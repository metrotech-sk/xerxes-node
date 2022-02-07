#ifndef XERXESLIB_H
#define	XERXESLIB_H

#include <vector>
#include <math.h>
#include <iostream>
//used for uart:
#include <unistd.h>			//Used for UART
#include <fcntl.h>			//Used for UART
#include <termios.h>		//Used for UART


class VectorOp
{
  public:
    template <class T, class U>
    static T v_sum(std::vector<U> &t_vec);

    template <class T, class U>
    static T v_average(std::vector<U> &t_vec);

    template <class T, class U>
    static T v_std_dev(std::vector<U> &t_vec, T t_average);

    template <class T, class U>
    static T v_max_err(std::vector<U> &t_vec, T t_average);

};

namespace Serial{

class RS485
{
  public:
    RS485(char *t_device, int t_baud, int tx_en);
    ~RS485();

    void setDevice(char *t_device);
    void setBaud(int t_baud);
    int openPort();
    void closePort();
    void writeChar(uint8_t t_send);
    u_char readChar();

  private:
    int uart0_filestream;
};

}

#ifdef	__cplusplus
extern "C" {
#endif
/* C only code goes here */ 

#ifdef	__cplusplus
}
#endif

#endif /* XERXESLIB_H */