#include "Stopwatch.hpp"


using namespace Xerxes;
using namespace std;
using namespace chrono;


Stopwatch::Stopwatch()
{
    ;
}

void Stopwatch::start()
{
    m_tp = std::chrono::high_resolution_clock::now();
}

void Stopwatch::setTimer(std::chrono::duration<double> t_duration)
{
    m_timer_duration = t_duration;
}

bool Stopwatch::elapsed()
{
    return duration_cast<std::chrono::duration<double>>(std::chrono::high_resolution_clock::now() - m_tp) > m_timer_duration;
}