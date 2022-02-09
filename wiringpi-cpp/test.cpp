#include <iostream>
#include <chrono>
#include <thread>
#include <termios.h>

#include "xerxeslib.hpp"
#include <wiringSerial.h>
#include <wiringPi.h>

using namespace std;
using namespace chrono;

class Stopwatch{
  public:
    high_resolution_clock::time_point m_tp;
    duration<double> m_timer_duration;
    Stopwatch()
    {
        ;
    }

    void start()
    {
        m_tp = high_resolution_clock::now();
    }

    void setTimer(duration<double> &t_duration)
    {
        m_timer_duration = t_duration;
    }

    bool elapsed()
    {
        return duration_cast<duration<double>>(high_resolution_clock::now() - m_tp) > m_timer_duration;
    }
};

int sendMsg(int &fd, vector<uint8_t> &msg, int &baud){
    if (fd < 0)
    {
        fprintf(stderr, "Unable to open UART");
        return -1;
    }

    auto t0 = high_resolution_clock::now();
    digitalWrite (1, HIGH) ;
    delayMicroseconds(1);
    for(auto el: msg){
        serialPutchar (fd, el) ;
    }
    auto t1 = high_resolution_clock::now();

    duration<double> time_span = duration_cast<duration<double>>(t1 - t0);
    auto sleepfor = (((double)msg.size()*10/baud)-time_span.count())*1000000;
    delayMicroseconds(sleepfor);
    digitalWrite (1, LOW) ;
    
    return 0;
}

vector<uint8_t> readMsg(const int &fd, duration<double> timeout){
    vector<uint8_t> to_return{0x01};
    Stopwatch sw = Stopwatch();
    sw.setTimer(timeout);
    sw.start();

    uint8_t header = 0x00;

    do
    {
        
        if(sw.elapsed())
        {
            return to_return;
        }
        header = serialGetchar(fd);
    }while(header != 0x01);

    uint8_t len = serialGetchar(fd);
    to_return.push_back(len);

    while(to_return.size() < len && !sw.elapsed()){
        // wait for the new data
        while(!serialDataAvail(fd));

        // receive data
        to_return.push_back(serialGetchar(fd));
    }

    return to_return;
}

int main(int argc, char** argv){

    //setup GPIO
    wiringPiSetup () ;
    pinMode (1, OUTPUT) ;

    using namespace std::chrono;

    uint32_t msgid(0);
    vector<uint8_t> devices{1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    std::vector<uint8_t> message;

    //open uart
    int baudrate = 115200;
    int fd = serialOpen("/dev/ttyS0", baudrate);
    
    // load UART options
    struct termios options ;
    tcgetattr (fd, &options) ;   // Read current options
    options.c_cc[VTIME] = 1;    // block for 100ms max
    options.c_cc[VMIN] = 0;
    tcsetattr (fd, TCSANOW, &options) ;   // Set new options

    try
    {
        
        while(true)
        {
            for(auto dst_dev:devices)
            {
                message = Xerxes::Protocol::craftMessage(0x00, dst_dev, msgid++);
                
                /*for(auto el:message)
                {
                    printf("%X, ", el);
                }
                cout << endl;*/
                sendMsg(fd, message, baudrate);

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
    
    serialClose(fd);

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
