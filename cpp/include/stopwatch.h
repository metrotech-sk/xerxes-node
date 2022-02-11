#ifndef STOPWATCH_H
#define STOPWATCH_H

#include <chrono>
#include <stdint.h>


namespace Xerxes{

class Stopwatch{
  public:
    std::chrono::high_resolution_clock::time_point m_tp;
    std::chrono::duration<double> m_timer_duration;
    Stopwatch();

    void start();

    void setTimer(std::chrono::duration<double> t_duration);

    bool elapsed();
};

}

#endif // STOPWATCH_H