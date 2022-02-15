#include "p_leaf.h"

using namespace std;
using namespace Xerxes;

PLeaf::PLeaf(const uint8_t &t_addr, Protocol *t_protocol, const chrono::duration<double> &t_std_timeout)
{
    my_addr = t_addr;
    m_protocol_ = t_protocol;
    std_timeout = t_std_timeout;
}

Readings &PLeaf::read()
{
    m_protocol_->ping(my_addr);
    // 01 1A 09 00 02 0000180A 00000097 00048F76 0006D223 00064262 73
    std::vector<uint8_t> rcvd;

    try
    {    
        rcvd = m_protocol_->read(std_timeout);
    }
    catch(runtime_error &e)
    {
        throw runtime_error("Unable to read sensor");
    }

    last_msg_id_ = (rcvd[5]*0x1000000) + (rcvd[6]*0x10000) + (rcvd[7]*0x100) + (rcvd[8]);
    last_reading_.pressure = MicroBar( (rcvd[9]*0x1000000) + (rcvd[10]*0x10000) + (rcvd[11]*0x100) + (rcvd[12]) );
    last_reading_.temp_sens = Kelvin( (rcvd[13]*0x1000000) + (rcvd[14]*0x10000) + (rcvd[15]*0x100) + (rcvd[16]) );
    last_reading_.temp_ext1 = Kelvin( (rcvd[17]*0x1000000) + (rcvd[18]*0x10000) + (rcvd[19]*0x100) + (rcvd[20]) );
    last_reading_.temp_ext2 = Kelvin( (rcvd[21]*0x1000000) + (rcvd[22]*0x10000) + (rcvd[23]*0x100) + (rcvd[24]) );
    
    
    m_ringbuf_ids_.push_back(last_msg_id_);
    if(m_ringbuf_ids_.size()>100)
    {
        m_ringbuf_ids_.erase(m_ringbuf_ids_.begin());
    }
    return last_reading_;
}


const double PLeaf::messagesReceived()
{
    return static_cast<double>(m_ringbuf_ids_.size()) / (m_ringbuf_ids_.back() - m_ringbuf_ids_.front() + 1);
}


const uint8_t &PLeaf::getAddr()
{
    return my_addr;
}


const uint32_t &PLeaf::getLastMsgId()
{
    return last_msg_id_;
}