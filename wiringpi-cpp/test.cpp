#include <iostream>
#include <chrono>
#include <thread>

#include <wiringPi.h>
#include <wiringSerial.h>
#include "xerxeslib.hpp"

using namespace std;

static auto pinval = HIGH;

void flip(int delayMicro){
    if(pinval == HIGH){
        pinval = LOW;
    }else{
        pinval = HIGH;
    }
    digitalWrite (0, pinval) ;
    delayMicroseconds(delayMicro);
}


void send_uart(){
    int fd = serialOpen("/dev/ttyAMA0", 115200);
    if (fd < 0)
    {
        fprintf(stderr, "Unable to open ttyAMA0");
    }

    serialPrintf(fd,"Hello World!!!\n");    
    cout << "fd is " << fd << endl;
    serialClose(fd);
}

int main(int argc, char** argv){
    wiringPiSetup () ;

    using namespace std::chrono;

    pinMode (0, OUTPUT) ;

    auto t = atoi(argv[1]);
    auto reps = atoi(argv[2]);

    vector<uint32_t> timings;
    // duration<double> time_span;
    nanoseconds time_span;

    high_resolution_clock::time_point t0, t1, t2;
    for(;;){
        t0 = high_resolution_clock::now();

        for(auto rep=0; rep<reps; rep++){
            t1 = high_resolution_clock::now();
            flip(t);
            t2 = high_resolution_clock::now();
            time_span = duration_cast<nanoseconds>(t2 - t1);
            timings.push_back(time_span.count());
        }

        /*
        for(auto el: timings){
            cout << (double)el/1000.0 << ", ";
        }
        cout << endl;*/

        auto average = VectorOp::v_average<double>(timings);
        auto std_dev = VectorOp::v_std_dev<double>(timings, average);
        auto desired_dev = VectorOp::v_std_dev<double>(timings, static_cast<double>(t)*1000);
        auto max_dev = VectorOp::v_max_err<double>(timings, static_cast<double>(t)*1000);

        cout << "Desired t[us]: " << t;
        cout <<", average t[us]:" << average/1000;
        cout << ", instability[us]: " << std_dev/1000;
        cout << ", inaccuracy[us]: " << desired_dev/1000;
        cout << ", max dev[us]: " << max_dev/1000 << endl;

        t2 = high_resolution_clock::now();
        time_span = duration_cast<milliseconds>(t2 - t0);
        auto sleepfor = static_cast<int>(1000-time_span.count()/1000000);
        std::this_thread::sleep_for(milliseconds(sleepfor));
        
    }
    return 0;
    
}
