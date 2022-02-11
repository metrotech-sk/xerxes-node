#include "p_leaf.h"

using namespace std;
using namespace Xerxes;

PLeaf::PLeaf(const uint8_t &t_addr, Protocol *t_protocol, const chrono::duration<double> &t_std_timeout)
{
    my_addr = t_addr;
    m_protocol = t_protocol;
    std_timeout = t_std_timeout;
}

Readings PLeaf::read()
{
    m_protocol->ping(my_addr);
    // 01 1A 09 00 02 0000180A 00000097 00048F76 0006D223 00064262 73
    auto rcvd = m_protocol->read(std_timeout);

    Readings vals;
    auto msgid = (rcvd[5]*0x1000000) + (rcvd[6]*0x10000) + (rcvd[7]*0x100) + (rcvd[8]);
    vals.p_bar = (rcvd[9]*0x1000000) + (rcvd[10]*0x10000) + (rcvd[11]*0x100) + (rcvd[12]);
    vals.t_sens = (rcvd[13]*0x1000000) + (rcvd[14]*0x10000) + (rcvd[15]*0x100) + (rcvd[16]);
    return vals;
}