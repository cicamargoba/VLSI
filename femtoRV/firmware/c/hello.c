#include <femtorv32.h>

int main() {
    char k = 0;
    char a = 0;
    for(k=1; k<= 10 ;k++){
        a = k + 2;
        print_hex(k);
        printf("\n\r");
        delay(50);
        
    }
     printf("\n\rHello C World!\n\r");
     while(1){
       *(volatile uint32_t*)(0x400010) = 4;
       delay(500);
       *(volatile uint32_t*)(0x400010) = 0;
      delay(500);
     }	
   return 0;
}

