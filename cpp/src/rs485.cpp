#include "rs485.h"

using namespace Xerxes;
using namespace std;
using namespace chrono;
using namespace LibSerial;


RS485::RS485(const string &t_device, GpioPin *tx_en)
{
    m_devname = t_device;
    pinTxEn_ = tx_en;

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
    my_serial_port.ReadByte( next_char, 1 );
	return next_char;
}


int RS485::writeMsg(const vector<uint8_t> &t_message)
{
    auto t0 = chrono::high_resolution_clock::now();
    
    pinTxEn_->SetHigh();


    for(auto el: t_message){
        writeChar(el);
    }

    auto t1 = high_resolution_clock::now();

    duration<double> time_span = duration_cast<duration<double>>(t1 - t0);
    auto sleepfor = (((double)t_message.size()*10/m_baudrate)-time_span.count())*1000000;

    usleep(sleepfor);

    pinTxEn_->SetLow();

    return t_message.size();
}


vector<uint8_t> RS485::readMsg(const chrono::duration<double> t_timeout)
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

    return to_return;
}
