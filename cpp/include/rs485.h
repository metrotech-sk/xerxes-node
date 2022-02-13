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
#include "gpio_pin.h"

namespace Xerxes{

class RS485: public Bus
{
  GpioPin *pinTxEn_;
  std::string m_devname;
  int m_baudrate{115200};

  public:

    RS485(const std::string &t_device, GpioPin *tx_en);
    ~RS485();


    int availChar();
    uint8_t readChar();
    void writeChar(const uint8_t &t_send);

    std::vector<uint8_t> readMsg(const std::chrono::duration<double> t_timeout);
    int writeMsg(const std::vector<uint8_t> &t_message);

  private:    
    LibSerial::SerialPort my_serial_port;

};

} // namespace Xerxes

#endif // RS485_H