#include "rs485.h"

using namespace Xerxes;
using namespace std;
using namespace chrono;

RS485::RS485(const string &t_device, const int &t_baud, const int &tx_en)
{
    //setup GPIO
    wiringPiSetup () ;
    pinMode (tx_en, OUTPUT) ;

	m_devname = t_device;
    m_txpin = tx_en;
    m_baudrate = t_baud;

}


/**
 * @brief close fd if opened
 * 
 */
RS485::~RS485(){
	if(m_uart_fd>0){
		serialClose(m_uart_fd);
	}
}


int RS485::openDevice(){
    // open uart
    
    m_uart_fd = serialOpen(m_devname.c_str(), m_baudrate);

    struct termios options ;
    tcgetattr (m_uart_fd, &options) ;   // Read current options
    options.c_cc[VTIME] = 0;    // block for 0ms max
    options.c_cc[VMIN] = 0;
    tcsetattr (m_uart_fd, TCSANOW, &options) ;   // Set new options
    return m_uart_fd;
}


void RS485::closeDevice()
{
	serialClose(m_uart_fd);
	m_uart_fd = -1;
}


bool RS485::opened()
{
	return (m_uart_fd > 0);
}


void RS485::writeChar(const uint8_t &t_send)
{
	if(opened())
	{
		serialPutchar(m_uart_fd, t_send);
	}
    else{
        cerr << "Uart not opened"<<endl;
    }
}


int RS485::availChar()
{
	return serialDataAvail(m_uart_fd);
}

uint8_t RS485::readChar()
{
	return static_cast<uint8_t>(serialGetchar(m_uart_fd));
}


void RS485::activateTx()
{
    digitalWrite (m_txpin, HIGH) ;
}


void RS485::deactivateTx()
{
    digitalWrite (m_txpin, LOW) ;
}


int RS485::writeMsg(const vector<uint8_t> &t_message)
{
    if (!opened())
    {
        cerr << "Unable to open: " << m_devname << endl;
        return -1;
    }

    auto t0 = chrono::high_resolution_clock::now();
    activateTx();
    
    delayMicroseconds(1);
    for(auto el: t_message){
        writeChar(el);
    }

    auto t1 = high_resolution_clock::now();

    duration<double> time_span = duration_cast<duration<double>>(t1 - t0);
    auto sleepfor = (((double)t_message.size()*10/m_baudrate)-time_span.count())*1000000;
    delayMicroseconds(sleepfor);
    
    deactivateTx();
    
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
