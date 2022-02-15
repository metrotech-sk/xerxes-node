#include "gpio_pin.h"

using namespace Xerxes;
using namespace std;

GpioPin::GpioPin(const int &pin_nr) : pin_nr_ {to_string(pin_nr)}
{
    Setup();
}

GpioPin::GpioPin(const string &pin_nr)
{
    Setup();
}


GpioPin::GpioPin(){
    ;
}


void GpioPin::Setup()
{
    // Export the desired pin by writing to /sys/class/gpio/export
    int fd = open("/sys/class/gpio/export", O_WRONLY);
    if (fd == -1) {
        cerr << "Unable to open /sys/class/gpio/export";
        exit(1);
    }

    if (write(fd, pin_nr_.c_str(), 2) != 2) {
        cerr << "Error writing to /sys/class/gpio/export";
        exit(1);
    }
    close(fd);

    // open pin value FD for write only
    pin_val_fd_ = open(("/sys/class/gpio/gpio"+pin_nr_+"/value").c_str(), O_WRONLY);
    if (fd == -1) {
        cerr << "Unable to open /sys/class/gpio/gpio"<<pin_nr_<<"/value";
        exit(1);
    }
}


GpioPin::~GpioPin()
{
    // Unexport the pin by writing to /sys/class/gpio/unexport

    close(pin_val_fd_);

    int fd = open("/sys/class/gpio/unexport", O_WRONLY);
    if (fd == -1) {
        cerr << "Unable to open /sys/class/gpio/unexport";
        exit(1);
    }

    if (write(fd, "18", 2) != 2) {
        cerr << "Error writing to /sys/class/gpio/unexport";
        exit(1);
    }

    close(fd);
}


void GpioPin::MakeOutput()
{
    // Set the pin to be an output by writing "out" to /sys/class/gpio/gpio24/direction

    int fd = open(("/sys/class/gpio/gpio"+pin_nr_+"/direction").c_str(), O_WRONLY);
    if (fd == -1) {
        cerr << "Unable to open /sys/class/gpio/gpio"<<pin_nr_<<"/direction";
        exit(1);
    }

    if (write(fd, "out", 3) != 3) {
        cerr << "Error writing to /sys/class/gpio/gpio"<<pin_nr_<<"/direction";
        exit(1);
    }

    close(fd);
}

void GpioPin::MakeInput()
{
    // Set the pin to be an input by writing "in" to /sys/class/gpio/gpio24/direction

    int fd = open(("/sys/class/gpio/gpio"+pin_nr_+"/direction").c_str(), O_WRONLY);
    if (fd == -1) 
    {
        cerr << "Unable to open /sys/class/gpio/gpio"<<pin_nr_<<"/direction";
        exit(1);
    }

    if (write(fd, "in", 3) != 3) 
    {
        cerr << "Error writing to /sys/class/gpio/gpio"<<pin_nr_<<"/direction";
        exit(1);
    }

    close(fd);
}


std::string GpioPin::GetDirection()
{
    // TODO (@themladypan) to implement
}


bool GpioPin::GetValue()
{
    // TODO (@themladypan) to implement
}


void GpioPin::SetLow()
{
    write(pin_val_fd_, "0", 1);
}


void GpioPin::SetHigh()
{
    write(pin_val_fd_, "1", 1);
}

