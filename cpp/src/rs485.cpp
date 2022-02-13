#include "rs485.h"
#include <libserial/SerialPort.h>

namespace Xerxes {

    RS485::RS485(const std::string &device) : pimpl(new LibSerial::SerialPort(device,
                                                                              LibSerial::BaudRate::BAUD_115200)){
        if (!pimpl->IsOpen()){
            throw std::runtime_error("Unable to ope device: " + device);
        }
    }

    std::vector<uint8_t> RS485::read(size_t maxSize, const std::chrono::milliseconds &timeout){
        std::vector<uint8_t> data;
        pimpl->Read(data, maxSize, timeout.count());
        return data;
    }

    size_t RS485::write(const std::vector<uint8_t> &data) {
        pimpl->Write(data);
        return data.size();
    }

}