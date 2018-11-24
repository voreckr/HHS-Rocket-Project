#include <wiringPi.h>

int main (void)

{

  wiringPiSetup () ;

  pinMode (18, OUTPUT) ;

  for (;;)

  {

    digitalWrite (18, HIGH) ; delay (1) ;

    digitalWrite (18,  LOW) ; delay (1) ;

  }

  return 0 ;

}

