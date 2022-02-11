#ifndef P_LEAF_H
#define P_LEAF_H

#include <stdint.h>
#include <vector>
#include <chrono>

#include <protocol.h>

namespace Xerxes
{

class Readings
{
  public:
    double p_bar;
    double t_sens;
    double t1;
    double t2;
};
    
class PLeaf{
  public:
    PLeaf(const uint8_t &t_addr, Protocol *t_protocol, const std::chrono::duration<double> &t_std_timeout);
    Readings read();
    uint8_t my_addr;
    std::chrono::duration<double> std_timeout;
    
  private:
    std::vector<uint32_t> m_ringbuf_ids;
    Protocol *m_protocol;

};

} // namespace Xerxes



#endif // P_LEAF_H