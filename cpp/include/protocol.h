#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <stdint.h>
#include <vector>
#include <numeric>
#include <chrono>

#include "bus.h"

#define SOH 0x01
#define SOT 0x02

namespace Xerxes{

class Protocol
{  
  public:
    Protocol(Bus *t_bus, const uint8_t &t_my_addr);
    ~Protocol();

    void ping(const uint8_t &t_destination);

    void send(const uint8_t &t_destination, const std::vector<uint8_t> &t_payload);
    void send(const uint8_t &t_destination, const std::vector<uint32_t> &t_payload);
    void send(const uint8_t &t_destination, const uint32_t &data);
    void send(const uint8_t &t_destination, const std::string &data);

    std::vector<uint8_t> read(const std::chrono::duration<double> &t_timeout);
    
    void readToBuf(std::vector<uint8_t> &t_buffer, const std::chrono::duration<double> &t_timeout);

    uint8_t my_addr;

  private:
    Bus *m_bus;

    std::vector<uint8_t> craftMessage(const uint8_t &t_dst, const std::vector<uint8_t> &payload);
    std::vector<uint8_t> craftPing(const uint8_t &t_dst);
    void addChecksum(std::vector<uint8_t> &buffer);
    void addWord(const uint32_t &t_word, std::vector<uint8_t> &t_buffer);


};

} // namespace Xerxes

#endif // PROTOCOL_H