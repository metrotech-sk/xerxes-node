#ifndef RS485_H
#define RS485_H

#include <string>
#include <stdint.h>
#include <unistd.h>
#include <thread>

#include <termios.h>
#include <libserial/SerialPort.h>

#include "bus.h"
#include "stopwatch.h"

namespace Xerxes{

class RS485: public Bus
{
  private:    
    LibSerial::SerialPort my_serial_port;
    std::string m_devname;
    int m_baudrate{115200};

    int availChar();
    uint8_t readChar();
    void writeChar(const uint8_t &t_send);

  public:

    RS485(const std::string &t_device);
    ~RS485();


    std::vector<uint8_t> read(const std::chrono::duration<double> t_timeout);
    int write(const std::vector<uint8_t> &t_message);


};

} // namespace Xerxes

#endif // RS485_H