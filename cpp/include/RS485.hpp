#ifndef RS485_H
#define RS485_H

#include <string>
#include <stdint.h>
#include <unistd.h>
#include <wiringPi.h>
#include <wiringSerial.h>
#include <termios.h>

#include "Bus.hpp"
#include "Stopwatch.hpp"

namespace Xerxes{

class RS485: public Bus
{
  public:
    std::string m_devname;
    int m_baudrate;

    RS485(const std::string &t_device, const int &t_baud, const int &tx_en);
    ~RS485();

    int openDevice();
    void closeDevice();
    bool opened();

    void writeChar(const uint8_t &t_send);

    int availChar();
    u_char readChar();

    void activateTx();
    void deactivateTx();

    std::vector<uint8_t> readMsg(const std::chrono::duration<double> t_timeout);
    int writeMsg(const std::vector<uint8_t> &t_message);
    int m_uart_fd = -1;
    int m_txpin;

};

} // namespace Xerxes

#endif // RS485_H