#ifndef P_LEAF_H
#define P_LEAF_H

#include <stdint.h>
#include <vector>
#include <chrono>

#include "protocol.h"
#include "pressure.h"
#include "temperature.h"


namespace Xerxes
{

class Readings
{
  public:
    Pressure pressure;
    Temperature temp_sens;
    Temperature temp_ext1;
    Temperature temp_ext2;
};




class PLeaf{
  private:
    Protocol *m_protocol_;
    Readings last_reading_;  
    uint8_t my_addr;
    double std_timeout;

  public:
    PLeaf(const uint8_t &t_addr, Protocol *t_protocol, const double &t_std_timeout);
    Readings &read();

    const uint8_t &getAddr();
};

} // namespace Xerxes



#endif // P_LEAF_H