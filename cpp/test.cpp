#include <iostream>
#include <chrono>
#include <thread>

#include "RS485.hpp"
#include "Protocol.hpp"

using namespace std;
using namespace chrono;

int main(int argc, char** argv){

    uint32_t msgid(0);
    vector<uint8_t> devices{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    vector<uint8_t> message;

    int rs_tx_enable_pin = 1;
    string ttyDev = "/dev/ttyS0";
    int baud = 115200;

    Xerxes::RS485 *rs485 = new Xerxes::RS485(ttyDev, baud, rs_tx_enable_pin);
    if(rs485->openDevice()<0)
    {
        cerr << "unable to open device: " <<ttyDev<<endl;
        return -1;
    };

    // open protocol, my addres 0x00;
    Xerxes::Protocol xerxes(rs485, 0x00);


    ;

    for(auto el:devices)
    {
        // message = xerxes.craftMessage(0x00, el, msgid++);
        
        // int sent = rs485->writeMsg(message);
        // this_thread::sleep_for(duration<double, micro>(atoi(argv[1])));
        //xerxes.sendUints(el, vector<uint32_t>{10,20,30,40});
        xerxes.ping(el);
        auto reply = rs485->readMsg(duration<double, milli>(atoi(argv[1])));
    }
    
/*
    try
    {
        
        while(true)
        {
            for(auto dst_dev:devices)
            {
                message = xerxes.craftMessage(0x00, dst_dev, msgid++);
                
                for(auto el:message)
                {
                    printf("%X, ", el);
                }
                cout << endl;

                xerxes.writeMsg(message);

                auto rcvd = readMsg(fd, duration<double>(0.010));
                
                printf("Reply: %X, size: %d, Chks: %X\n", dst_dev, (int)rcvd.size(), VectorOp::v_sum<uint8_t>(rcvd));
                delayMicroseconds(500);
            }
        }
    }
    catch(const std::exception& e)
    {
        std::cerr << e.what() << '\n';
    }
    */

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
