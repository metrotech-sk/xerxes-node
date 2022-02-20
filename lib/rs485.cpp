#include "rs485.h"

using namespace Xerxes;
using namespace std;
using namespace chrono;
using namespace LibSerial;


RS485::RS485(const string &t_device)
{
    m_devname = t_device;

    my_serial_port.Open(t_device);

    my_serial_port.SetBaudRate( BaudRate::BAUD_115200 );
    my_serial_port.SetCharacterSize( CharacterSize::CHAR_SIZE_8 );
    my_serial_port.SetParity( Parity::PARITY_NONE );
    my_serial_port.SetStopBits( StopBits::STOP_BITS_1 );
}

/**
 * @brief close fd if opened
 * 
 */
RS485::~RS485(){
    if(my_serial_port.IsOpen())
    {
        my_serial_port.Close();
    }
}


void RS485::writeChar(const uint8_t &t_send)
{
    my_serial_port.WriteByte( t_send );
}


int RS485::availChar()
{
	return my_serial_port.GetNumberOfBytesAvailable();
}

uint8_t RS485::readChar()
{
    uint8_t next_char;
    try
    {
        my_serial_port.ReadByte( next_char, 1 );
    }
    catch(LibSerial::ReadTimeout)
    {
        next_char = 0x00;
    }
	return next_char;
}


int RS485::write(const vector<uint8_t> &t_message)
{

    
    for(auto el: t_message){
        writeChar(el);
    }


    return t_message.size();
}


vector<uint8_t> RS485::read(const chrono::duration<double> t_timeout)
{
	vector<uint8_t> to_return;
    Stopwatch sw = Stopwatch();
    sw.setTimer(t_timeout);
    sw.start();

	// wait for SOH header char:
    uint8_t header = 0x00;
    do
    {        
        if(sw.elapsed())
        {
            return to_return;
        }
        header = readChar();
    }while(header != 0x01);

    to_return.push_back(0x01);

	while(!availChar() && !sw.elapsed());
    uint8_t len = readChar();
    to_return.push_back(len);

    while(to_return.size() < len && !sw.elapsed()){
        // wait for the new data
        while(!availChar() && !sw.elapsed());

        // receive data
        to_return.push_back(readChar());
    }
    if(sw.elapsed())
    {
        throw runtime_error("Message read timed out");
    }

    return to_return;
}
