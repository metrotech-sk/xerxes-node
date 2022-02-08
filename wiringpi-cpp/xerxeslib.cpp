#include "xerxeslib.hpp"

using namespace std;

template <class T, class U>
T VectorOp::v_sum(vector<U> &t_vec){
    T sum = 0;
    for(auto el: t_vec){
        sum += el;
    }
    return sum;
}


template <class T, class U>
T VectorOp::v_average(vector<U> &t_vec){
    return static_cast<T>(v_sum<T>(t_vec))/t_vec.size();
}


template <class T, class U>
T VectorOp::v_std_dev(vector<U> &t_vec, T t_average){
    vector<T> v_err2;
    T err2;
    for(auto el: t_vec){
        v_err2.push_back(pow((el - t_average), 2));
    }
    return sqrt(v_sum<T>(v_err2))/t_vec.size();
}


template <class T, class U>
T VectorOp::v_max_err(vector<U> &t_vec, T t_average){
    long double ldmax = -__LDBL_MAX__;
    for(auto el: t_vec){
        if(abs(el - t_average) > ldmax){
            ldmax = abs(el - t_average);
        }
    }
    return ldmax;
}


Xerxes::RS485::RS485(string &t_device, int &t_baud, int &tx_en)
{
    /*
    //-------------------------
	//----- SETUP USART 0 -----
	//-------------------------
	//At bootup, pins 8 and 10 are already set to UART0_TXD, UART0_RXD (ie the alt0 function) respectively
	uart0_filestream = -1;
	
	//OPEN THE UART
	//The flags (defined in fcntl.h):
	//	Access modes (use 1 of these):
	//		O_RDONLY - Open for reading only.
	//		O_RDWR - Open for reading and writing.
	//		O_WRONLY - Open for writing only.
	//
	//	O_NDELAY / O_NONBLOCK (same function) - Enables nonblocking mode. When set read requests on the file can return immediately with a failure status
	//											if there is no input immediately available (instead of blocking). Likewise, write requests can also return
	//											immediately with a failure status if the output can't be written immediately.
	//
	//	O_NOCTTY - When set and path identifies a terminal device, open() shall not cause the terminal device to become the controlling terminal for the process.

	uart0_filestream = open(t_device, O_RDWR | O_NOCTTY | O_NDELAY);		//Open in non blocking read/write mode
	if (uart0_filestream == -1)
	{
		//ERROR - CAN'T OPEN SERIAL PORT
		std::cerr << "Error - Unable to open UART.  Ensure it is not in use by another application" << std::endl;
	}
	
	//CONFIGURE THE UART
	//The flags (defined in /usr/include/termios.h - see http://pubs.opengroup.org/onlinepubs/007908799/xsh/termios.h.html):
	//	Baud rate:- B1200, B2400, B4800, B9600, B19200, B38400, B57600, B115200, B230400, B460800, B500000, B576000, B921600, B1000000, B1152000, B1500000, B2000000, B2500000, B3000000, B3500000, B4000000
	//	CSIZE:- CS5, CS6, CS7, CS8
	//	CLOCAL - Ignore modem status lines
	//	CREAD - Enable receiver
	//	IGNPAR = Ignore characters with parity errors
	//	ICRNL - Map CR to NL on input (Use for ASCII comms where you want to auto correct end of line characters - don't use for bianry comms!)
	//	PARENB - Parity enable
	//	PARODD - Odd parity (else even)
	struct termios options;
	tcgetattr(uart0_filestream, &options);
	options.c_cflag = B9600 | CS8 | CLOCAL | CREAD;		//<Set baud rate
	options.c_iflag = IGNPAR;
	options.c_oflag = 0;
	options.c_lflag = 0;
	tcflush(uart0_filestream, TCIFLUSH);
	tcsetattr(uart0_filestream, TCSANOW, &options);

    */


    uart0_filestream = serialOpen("/dev/ttyS0", 115200);
}

void Xerxes::RS485::writeChar(uint8_t t_send)
{
    	//----- TX BYTES -----
	unsigned char tx_buffer[20];
	unsigned char *p_tx_buffer;
	
	p_tx_buffer = &tx_buffer[0];
	*p_tx_buffer++ = 'H';
	*p_tx_buffer++ = 'e';
	*p_tx_buffer++ = 'l';
	*p_tx_buffer++ = 'l';
	*p_tx_buffer++ = 'o';
	
	if (this->uart0_filestream != -1)
	{
		int count = write(uart0_filestream, &tx_buffer[0], (p_tx_buffer - &tx_buffer[0]));		//Filestream, bytes to write, number of bytes to write
		if (count < 0)
		{
			printf("UART TX error\n");
		}
	}
}

uint8_t Xerxes::RS485::readChar()
{
    	//----- CHECK FOR ANY RX BYTES -----
	if (uart0_filestream != -1)
	{
		// Read up to 255 characters from the port if they are there
		uint8_t rx_buffer[1];
		int rx_length = read(uart0_filestream, (void*)rx_buffer, 1);		//Filestream, buffer to store in, number of bytes to read (max)
		if (rx_length < 0)
		{
			//An error occured (will occur if there are no bytes)
		}
		else if (rx_length == 0)
		{
			//No data waiting
		}
		else
		{
			//Bytes received
            return rx_buffer[0];
		}
	}
    return 0;
}

void Xerxes::RS485::activateTx()
{
    digitalWrite (0, HIGH) ;
}

void Xerxes::RS485::deactivateTx()
{
    digitalWrite (0, LOW) ;
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
std::vector<uint8_t> Xerxes::Protocol::craftMessage(const uint8_t &t_src, const uint8_t &t_dst, const uint32_t &messageId, const std::vector<uint8_t> &payload)
{
    std::vector<uint8_t> message;
    message.push_back(SOH);
    message.push_back(payload.size() + 10);
    message.push_back(t_src);
    message.push_back(t_dst);
    message.push_back(SOT);

    // convert msg id to chars - big endian style
    addWord(messageId, message);

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
std::vector<uint8_t> Xerxes::Protocol::craftMessage(const uint8_t &t_src, const uint8_t &t_dst, const uint32_t &messageId)
{
    std::vector<uint8_t> message;
    message.push_back(SOH);
    message.push_back(10);
    message.push_back(t_src);
    message.push_back(t_dst);
    message.push_back(SOT);

    // convert msg id to chars - big endian style
    addWord(messageId, message);  
    addChecksum(message);
    return message;
}

/**
 * @brief split uint32_t into bytes and append it to the buffer
 * 
 * @param t_word uint32_t to split
 * @param buffer the buffer on which it will be appened
 */
void Xerxes::Protocol::addWord(const uint32_t &t_word, std::vector<uint8_t> &buffer){
    buffer.push_back((t_word&0xFF000000) >> 24);
    buffer.push_back((t_word&0x00FF0000) >> 16);
    buffer.push_back((t_word&0x0000FF00) >>  8);
    buffer.push_back((t_word&0x000000FF) >>  0);
}

/**
 * @brief calculate checksum of provided buffer, then append it to the end
 * 
 * @param buffer 
 */
void Xerxes::Protocol::addChecksum(std::vector<uint8_t> &buffer)
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

// these will be used later:
template double VectorOp::v_average<double, unsigned int>(std::vector<unsigned int, std::allocator<unsigned int> >&);
template double VectorOp::v_std_dev<double, unsigned int>(std::vector<unsigned int, std::allocator<unsigned int> >&, double);
template double VectorOp::v_max_err<double, unsigned int>(std::vector<unsigned int, std::allocator<unsigned int> >&, double);