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
    virtual std::vector<uint8_t> read(const std::chrono::duration<double> t_timeout) = 0;
    virtual int write(const std::vector<uint8_t> &t_message) = 0;
};

} // namespace Xerxes

#endif //BUS_H
