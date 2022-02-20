#include "vectorop.h"

using namespace std;

template <class T, class U>
T VectorOp::v_sum(vector<U> &t_vec){
    T sum = 0;
    for(auto el: t_vec){
        sum += el;
    }
    return sum;
}


template <class T, class U>
T VectorOp::v_average(vector<U> &t_vec){
    return static_cast<T>(v_sum<T>(t_vec))/t_vec.size();
}


template <class T, class U>
T VectorOp::v_std_dev(vector<U> &t_vec, T t_average){
    vector<T> v_err2;
    T err2;
    for(auto el: t_vec){
        v_err2.push_back(pow((el - t_average), 2));
    }
    return sqrt(v_sum<T>(v_err2))/t_vec.size();
}


template <class T, class U>
T VectorOp::v_max_err(vector<U> &t_vec, T t_average){
    long double ldmax = -__LDBL_MAX__;
    for(auto el: t_vec){
        if(abs(el - t_average) > ldmax){
            ldmax = abs(el - t_average);
        }
    }
    return ldmax;
}


// these will be used later:
template double VectorOp::v_average<double, unsigned int>(std::vector<unsigned int, std::allocator<unsigned int> >&);
template double VectorOp::v_std_dev<double, unsigned int>(std::vector<unsigned int, std::allocator<unsigned int> >&, double);
template double VectorOp::v_max_err<double, unsigned int>(std::vector<unsigned int, std::allocator<unsigned int> >&, double);
template uint8_t VectorOp::v_sum<uint8_t, uint8_t>(std::vector<uint8_t> &);
