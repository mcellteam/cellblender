/* File : rng.h */

#include <iostream>
#include <string>

#include <inttypes.h>

using namespace std;

class MCellRandomNumber {
 public:
  virtual double rng_gauss();
};

#define rot(x, k) (((x) << (k)) | ((x) >> (32 - (k))))

class MCellRandomNumber_mrng : public MCellRandomNumber {
 private:
  uint32_t a;
  uint32_t b;
  uint32_t c;
  uint32_t d;
 public:
  MCellRandomNumber_mrng ( uint32_t seed );
  uint32_t generate();
  //double rng_gauss();
};
