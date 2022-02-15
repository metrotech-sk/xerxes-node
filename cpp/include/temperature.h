#ifndef TEMPERATURE_H
#define TEMPERATURE_H

#include <stdint.h>

class Temperature
{
  protected:
    double k_;

  public:
    Temperature() : k_{0}{}
    const double getCelsius(){
      return k_ - 273.15;
    }
    const double &getKelvin(){
      return k_;
    }
};

class Kelvin : public Temperature
{
  public:
    Kelvin(const uint32_t &millikelvin)
    {
        k_ = static_cast<double>(millikelvin) / 1000;
    }
};

class Celsius : public Temperature
{
  public:
    Celsius(const uint32_t &t_celsius)
    {
        k_ = t_celsius + 273.15;
    }
};

#endif //TEMPERATURE_H