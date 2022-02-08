#include <iostream>
#include <chrono>
#include <thread>

#include "xerxeslib.hpp"
#include <wiringSerial.h>
#include <wiringPi.h>

using namespace std;


int sendMsg(vector<uint8_t> msg){
    int baudrate = 115200;
    int fd = serialOpen("/dev/ttyS0", baudrate);
    if (fd < 0)
    {
        fprintf(stderr, "Unable to open UART");
        return -1;
    }

    digitalWrite (1, HIGH) ;
    delayMicroseconds(1);
    for(auto el: msg){
        serialPutchar (fd, 0x01) ;
    }
    delayMicroseconds(msg.size()*10000000/baudrate);
    digitalWrite (1, LOW) ;
    serialClose(fd);
    return 0;
}

int main(int argc, char** argv){
    wiringPiSetup () ;
    pinMode (1, OUTPUT) ;

    using namespace std::chrono;

    uint32_t msgid(0);
    vector<uint8_t> devices{0x01, 0x02, 0x03};

    for(auto dst_dev:devices)
    {
        std::vector<uint8_t> message = Xerxes::Protocol::craftMessage(0x00, dst_dev, msgid++);
        
        for(auto el:message)
        {
            printf("%X, ", el);
        }
        cout << endl;
        sendMsg(message);
    }


    return 0;

    // vector<uint32_t> timings;
    // duration<double> time_span;
    // nanoseconds time_span;

    // high_resolution_clock::time_point t0, t1, t2;
    
    // t0 = high_resolution_clock::now();
    // time_span = duration_cast<nanoseconds>(t2 - t1);
    // auto sleepfor = static_cast<int>(1000-time_span.count()/1000000);
    // std::this_thread::sleep_for(milliseconds(sleepfor));
    
    return 0;
    
}
