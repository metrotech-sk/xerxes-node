#include "Protocol.hpp"


/* PROTOCOL DEFINITIONS BEGINS HERE */

using namespace Xerxes;
using namespace std;

Protocol::Protocol(Bus *t_bus, const uint8_t &t_my_addr){
	m_bus = t_bus;
    m_my_addr = t_my_addr;
}


Protocol::~Protocol()
{
	;
}


/**
 * @brief Generate message suitable for RS485 xerxes protocol
 * 
 * @param t_src Source device address
 * @param t_dst Destination device address
 * @param messageId Message ID, usually consecutive
 * @param payload Actual data to send
 * @return std::vector<uint8_t> the crafted message suitable for transmission
 */
std::vector<uint8_t> Protocol::craftMessage(const uint8_t &t_src, const uint8_t &t_dst, const std::vector<uint8_t> &payload)
{
    std::vector<uint8_t> message;
    message.push_back(SOH);
    message.push_back(payload.size() + 6);
    message.push_back(t_src);
    message.push_back(t_dst);
    message.push_back(SOT);

    // convert msg id to chars - big endian style
    for(auto el: payload)
    {
        message.push_back(el);
    }
    
    addChecksum(message);
    return message;
}


/**
 * @brief create empty message for device, for xerxes network
 * 
 * @param t_src Source device address
 * @param t_dst Destination device address
 * @param messageId message id
 * @return std::vector<uint8_t> crafted message
 */
vector<uint8_t> Protocol::craftPing(const uint8_t &t_src, const uint8_t &t_dst)
{
    vector<uint8_t> message;
    message.push_back(SOH);
    message.push_back(6);
    message.push_back(t_src);
    message.push_back(t_dst);
    message.push_back(SOT);

    // convert msg id to chars - big endian style
    addChecksum(message);
    return message;
}

/**
 * @brief split uint32_t into bytes and append it to the buffer
 * 
 * @param t_word uint32_t to split
 * @param buffer the buffer on which it will be appened
 */
void Protocol::addWord(const uint32_t &t_word, vector<uint8_t> &t_buffer){
    t_buffer.push_back((t_word&0xFF000000) >> 24);
    t_buffer.push_back((t_word&0x00FF0000) >> 16);
    t_buffer.push_back((t_word&0x0000FF00) >>  8);
    t_buffer.push_back((t_word&0x000000FF) >>  0);
}

/**
 * @brief calculate checksum of provided buffer, then append it to the end
 * 
 * @param buffer 
 */
void Protocol::addChecksum(vector<uint8_t> &buffer)
{
    uint8_t summary = 0;
    for(auto el: buffer)
    {
        summary += el;
    }
    
    summary ^= 0xFF;  // get complement of summary
    summary++;  // get 2's complement
    summary %= 0x100;  // get last 8 bits of summary
    buffer.push_back(summary);
}


void Protocol::sendUints(const uint8_t &t_destination, const vector<uint32_t> &t_payload)
{
    vector<uint8_t> buffer;
    for(auto el:t_payload)
    {
        addWord(el, buffer);
    }

    auto message = craftMessage(m_my_addr, t_destination, buffer);
    m_bus->writeMsg(message);
}


void Protocol::sendUint(const uint8_t &t_destination, const uint32_t &data)
{    
    vector<uint8_t> buffer;
    addWord(data, buffer);

    auto message = craftMessage(m_my_addr, t_destination, buffer);
    m_bus->writeMsg(message);

}

void Protocol::ping(const uint8_t &t_destination)
{

    m_bus->writeMsg(craftPing(m_my_addr, t_destination));
}