#include "Bus.hpp"

using namespace Xerxes;


bool Bus::opened()
{
    return false;
}


std::vector<uint8_t> Bus::readMsg(const std::chrono::duration<double> t_timeout)
{
    return std::vector<uint8_t>();
}


int Bus::writeMsg(const std::vector<uint8_t> &t_message)
{   
    throw std::runtime_error("Redefine this");
}
