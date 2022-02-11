#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <vector>
#include <chrono>

#include "Bus.hpp"


#define SOH 0x01
#define SOT 0x02

namespace Xerxes{

class Protocol: public Bus
{  
  public:
    Protocol(Bus *t_bus, const uint8_t &t_my_addr);
    ~Protocol();

    void ping(const uint8_t &t_destination);

    void sendUints(const uint8_t &t_destination, const std::vector<uint32_t> &t_payload);
    void sendUint(const uint8_t &t_destination, const uint32_t &data);

    uint8_t m_my_addr;
  private:
    Bus *m_bus;

    std::vector<uint8_t> craftMessage(const uint8_t &t_src, const uint8_t &t_dst, const std::vector<uint8_t> &payload);
    std::vector<uint8_t> craftPing(const uint8_t &t_src, const uint8_t &t_dst);
    void addChecksum(std::vector<uint8_t> &buffer);
    void addWord(const uint32_t &t_word, std::vector<uint8_t> &t_buffer);


};

} // namespace Xerxes

#endif // PROTOCOL_H