#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <math.h>

#include <wiringPi.h>
#include <wiringSerial.h>

using namespace std;

static auto pinval = HIGH;

void flip(int delayMicro){
    pinval = ~pinval;
    digitalWrite (0, pinval) ;
    delayMicroseconds(delayMicro);
}


template <class T, class U>
T v_sum(vector<U> &t_vec){
    T sum = 0;
    for(auto el: t_vec){
        sum += el;
    }
    return sum;
}


template <class T, class U>
T v_average(vector<U> &t_vec){
    return static_cast<T>(v_sum<T>(t_vec))/t_vec.size();
}


template <class T, class U>
T v_std_dev(vector<U> &t_vec, T t_average){
    vector<T> v_err2;
    T err2;
    for(auto el: t_vec){
        v_err2.push_back(pow((el - t_average), 2));
    }
    return sqrt(v_sum<T>(v_err2))/t_vec.size();
}


template <class T, class U>
T v_max_err(vector<U> &t_vec, T t_average){
    long double ldmax = -__LDBL_MAX__;
    for(auto el: t_vec){
        if(abs(el - t_average) > ldmax){
            ldmax = abs(el - t_average);
        }
    }
    return ldmax;
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

        auto average = v_average<double>(timings);
        auto std_dev = v_std_dev<double>(timings, average);
        auto desired_dev = v_std_dev<double>(timings, static_cast<double>(t)*1000);
        auto max_dev = v_max_err<double>(timings, static_cast<double>(t)*1000);

        cout << "Desired t[us]: " << t;
        cout <<", average t[us]:" << average/1000;
        cout << ", instability[us]: " << std_dev/1000;
        cout << ", inaccuracy[us]: " << desired_dev/1000;
        cout << ", max dev[us]: " << max_dev/1000 << endl;

        t2 = high_resolution_clock::now();
        time_span = duration_cast<milliseconds>(t2 - t0);
        std::this_thread::sleep_for(chrono::milliseconds(static_cast<int>(1000-time_span.count()*1000)));
        
    }
    return 0;
    
}
