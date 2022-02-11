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
    virtual bool opened();
    virtual std::vector<uint8_t> readMsg(const std::chrono::duration<double> t_timeout);
    virtual int writeMsg(const std::vector<uint8_t> &t_message);
};

} // namespace Xerxes

#endif //BUS_H
