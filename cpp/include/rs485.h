#ifndef RS485_H
#define RS485_H

#include <memory>
#include "bus.h"
namespace LibSerial {
    class SerialPort;
}
namespace Xerxes {

    class RS485 : public Bus {
    public:
        //todo expose parameters;
        RS485(const std::string &device);

        std::vector<uint8_t> read(size_t maxSize, const std::chrono::milliseconds &timeout) override;

        size_t write(const std::vector<uint8_t> &data) override;

    private:
        std::unique_ptr<LibSerial::SerialPort> pimpl;
    };

} // namespace Xerxes

#endif // RS485_H