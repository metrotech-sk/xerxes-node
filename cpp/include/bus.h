#ifndef BUS_H
#define BUS_H

#include <stdint.h>
#include <vector>
#include <chrono>
#include <iostream>

namespace Xerxes
{
    
class Bus
{
  public:
    virtual std::vector<uint8_t> read(size_t maxSize, const std::chrono::milliseconds& timeout) = 0;
    virtual size_t write(const std::vector<uint8_t> &t_message) = 0;
};

} // namespace Xerxes

#endif //BUS_H
