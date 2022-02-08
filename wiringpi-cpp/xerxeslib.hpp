#ifndef XERXESLIB_H
#define	XERXESLIB_H

#include <vector>
#include <math.h>
#include <iostream>

#include <wiringPi.h>
#include <wiringSerial.h>

//used for uart:
#include <unistd.h>			//Used for UART
#include <fcntl.h>			//Used for UART
#include <termios.h>		//Used for UART


#define SOH 0x01
#define SOT 0x02

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

namespace Xerxes{

class Protocol
{  
  public:
    static std::vector<uint8_t> craftMessage(const uint8_t &t_src, const uint8_t &t_dst, const uint32_t &messageId, const std::vector<uint8_t> &payload);
    static std::vector<uint8_t> craftMessage(const uint8_t &t_src, const uint8_t &t_dst, const uint32_t &messageId);
    static void addChecksum(std::vector<uint8_t> &buffer);
    static void addWord(const uint32_t &t_word, std::vector<uint8_t> &buffer);

};

class RS485
{
  public:
    RS485(std::string &t_device, int &t_baud, int &tx_en);
    ~RS485();

    int openPort();
    void closePort();
    void writeChar(uint8_t t_send);
    //void sendMessage(std::vector<uint8_t> &message);
    u_char readChar();
    void activateTx();
    void deactivateTx();

  private:
    int uart0_filestream;
    int txpin;
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