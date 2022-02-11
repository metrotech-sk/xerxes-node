#ifndef VECTOR_OP_H
#define VECTOR_OP_H

#include <vector>
#include <stdint.h>
#include <math.h>

class VectorOp
{
  public:
    template <class T, class U>
    static T v_sum(std::vector<U> &t_vec);

    template <class T, class U>
    static T v_average(std::vector<U> &t_vec);

    template <class T, class U>
    static T v_std_dev(std::vector<U> &t_vec, T t_average);

    template <class T, class U>
    static T v_max_err(std::vector<U> &t_vec, T t_average);

};

#endif // VECTOR_OP_H