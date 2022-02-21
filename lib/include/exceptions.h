#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <exception>
#include <string>
#include <sstream>


namespace Xerxes{


class TimeoutExpired : public std::exception
{
  private:
    std::string message;

  public:
    TimeoutExpired()
    {
        message = "Timeout Expired";
    }
    TimeoutExpired(const std::string &t_message)
    {
        message = t_message;
    };

	const char * what () const throw ()
    {
    	return message.c_str();
    }
};


class InvalidMessageLength : public std::exception
{
  private:
    std::string message;
    int expected{0};
    int received{0};

  public:
    InvalidMessageLength()
    {
        message = "InvalidMessage";
    };

    InvalidMessageLength(const std::string &t_message)
    {
        message = t_message;
    };

    InvalidMessageLength(const std::string &t_message, const int t_expected, const int t_received)
    {
        message = t_message;
        expected = t_expected;
        received = t_received;
    };

	const char * what () const throw ()
    {
        if(expected != 0){
            std::stringstream to_return{message};
            to_return << "expected: " << expected << ", received: " << received;
            return to_return.str().c_str();
        }
    	return message.c_str();
    }
};


class InvalidMessageChecksum : public std::exception
{
  private:
    std::string message;
    uint8_t calculated{0};

  public:
    InvalidMessageChecksum()
    {
        message = "InvalidMessage";
    };

    InvalidMessageChecksum(const std::string &t_message)
    {
        message = t_message;
    };

    InvalidMessageChecksum(const std::string &t_message, const uint8_t t_calculated)
    {
        message = t_message;
        calculated = t_calculated;
    };

	const char * what () const throw ()
    {
        if(calculated != 0){
            std::stringstream to_return{message};
            to_return << ", calculated: " << calculated;
            return to_return.str().c_str();
        }
    	return message.c_str();
    }
};

} // namespace Xerxes


#endif //EXCEPTIONS_H