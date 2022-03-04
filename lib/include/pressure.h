#ifndef PRESSURE_H
#define PRESSURE_H

#include <stdint.h>

class Pressure
{
  protected:
    double bar_;
  public:
    Pressure() : bar_{0}
    {

    }
    Pressure(const double &t_bar) : bar_{t_bar}
    {

    }
    const double &getBar()
    {
      return bar_;
    }
    const double getmmH2O()
    {
      return bar_ * 10197.162129779;
    }
};

class MicroBar: public Pressure
{
  public:
    MicroBar(const uint32_t &microbar)
    {
      this->bar_ = static_cast<double>(microbar)/1000000;
    }
};

#endif //PRESSURE_H