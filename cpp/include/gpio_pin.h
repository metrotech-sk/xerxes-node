#ifndef GPIO_PIN_H
#define GPIO_PIN_H

#include <string>
#include <iostream>

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>


namespace Xerxes
{

class GpioPin
{
    std::string direction_;
    std::string pin_nr_{};
    int pin_val_fd_;

  public:
    GpioPin();
    GpioPin(const int &pin_nr);
    GpioPin(const std::string &pin_nr);
    ~GpioPin();

    void MakeOutput();
    void MakeInput();

    std::string GetDirection();

    bool GetValue();
    void SetLow();
    void SetHigh();
  
  private:
    void Setup();
};

}

#endif //GPIO_PIN_H