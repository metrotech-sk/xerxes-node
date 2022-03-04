#include <iostream>
#include <chrono>
#include <thread>
#include <vector>


#include "rs485.h"
#include "protocol.h"
#include "p_leaf.h"

#include <libserial/SerialPort.h>

using namespace std;
using namespace chrono;
using namespace LibSerial;

int main(int argc, char** argv){
    vector<uint8_t> addresses{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    vector<Xerxes::PLeaf> leaves;

    uint8_t next_char;

    cout << argv[0] << endl;

    string ttyDev = string{argv[1]};
    cout << "using: " << ttyDev << endl;
    duration<double, milli> timeout{atoi(argv[2])};

    Xerxes::RS485 *rs485 = new Xerxes::RS485(ttyDev);

    // open protocol, my addres 0x00;
    Xerxes::Protocol *xerxes = new Xerxes::Protocol(rs485, 0x00);


    // Xerxes::PLeaf snimac1(0x01, xerxes, duration<double, milli>(20));

    for(auto addr:addresses){
        leaves.push_back(Xerxes::PLeaf(addr, xerxes, timeout));
    }

    Xerxes::Readings lval;

    for (;;)
    {
        high_resolution_clock::time_point start = high_resolution_clock::now();
        cout << endl<<endl;

        for(auto leaf:leaves)
        {
            try
            {
                lval = leaf.read();
                cout << "P: " << lval.pressure.getmmH2O() << ", ts: " << lval.temp_sens.getCelsius();
                cout << ", tx1: " << lval.temp_ext1.getCelsius() << ", tx2: " << lval.temp_ext2.getCelsius() << endl;
            }
            catch(runtime_error &e)
            {
                cerr << static_cast<int>(leaf.getAddr()) << " - inaccessible!" << endl;
            }
        }
        duration<double> ex_time = duration_cast<duration<double>>( high_resolution_clock::now() - start );
        std::this_thread::sleep_for(duration<double>(1) - ex_time);
    }

    
    vector<uint8_t>buf;

/*
    for (;;)
    {
        for(auto el:devices)
        {
            // this_thread::sleep_for(duration<double, micro>(atoi(argv[1])));
            buf.erase(buf.begin(), buf.end());
            xerxes.ping(el);
            try{
                xerxes.readToBuf(buf, duration<double, milli>(atoi(argv[1])));
                if(buf.size()>0)
                {
                    cout<<"msg from";
                    printf("[%.2X]", el);
                    cout << ": ";
                    for(auto el:buf)
                    {
                        printf("%.2X", el);
                    }
                    cout<<endl;
                }
            }
            catch (runtime_error &e)
            {
                cerr << e.what();
                cout << "Invalid data received from";
                printf("%.2X\n", el);
                this_thread::sleep_for(duration<double, milli>(1000));
            }
        }
        this_thread::sleep_for(duration<double, milli>(100));
    }
    */
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
