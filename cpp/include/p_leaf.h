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
    uint32_t last_msg_id_ {0};
    std::vector<uint32_t> m_ringbuf_ids_;
    uint8_t my_addr;
    std::chrono::duration<double> std_timeout;

  public:
    PLeaf(const uint8_t &t_addr, Protocol *t_protocol, const std::chrono::duration<double> &t_std_timeout);
    Readings &read();

    const double messagesReceived();
    const uint8_t &getAddr();
    const uint32_t &getLastMsgId();
};

} // namespace Xerxes



#endif // P_LEAF_H