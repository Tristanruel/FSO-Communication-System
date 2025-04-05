#include <Arduino.h>
#include <IRremote.h>


#define IR_SEND_PIN 2


IRsend myIRsender;

const char* message = "Hello World!  ";

static const unsigned int MY_NEC_HEADER_MARK  = 9000;
static const unsigned int MY_NEC_HEADER_SPACE = 4500;
static const unsigned int MY_NEC_BIT_MARK     = 560;
static const unsigned int MY_NEC_ONE_SPACE    = 1690;
static const unsigned int MY_NEC_ZERO_SPACE   = 560;
static const unsigned int MY_NEC_TRAILER_MARK = 560;


void setup() {
 Serial.begin(9600);
 Serial.println("NEC Transmitter Ready");
 myIRsender.begin(IR_SEND_PIN);

 delay(1000);
}


void loop() {
 sendHelloWorld();
 delay(5000);
}


void sendHelloWorld() {
 Serial.println("Sending 'Hello World' via NEC:");
 const char* p = message;
 while (*p) {
   uint8_t address    = 0x00;
   uint8_t command    = (uint8_t)*p;
   uint8_t addressInv = ~address;
   uint8_t commandInv = ~command;


   uint32_t data = ((uint32_t)address    << 24) |
                   ((uint32_t)addressInv << 16) |
                   ((uint32_t)command    <<  8) |
                    (uint32_t)commandInv;

   myIRsender.sendNEC(data, 32, 0);


   Serial.print("  Sent char '");
   Serial.print(*p);
   Serial.print("' (ASCII 0x");
   Serial.print(command, HEX);
   Serial.println(")");

   printNECPulseTrain(data);


   p++;
   delay(100);
 }

 {
   uint8_t address    = 0x00;
   uint8_t command    = 0x00; 
   uint8_t addressInv = ~address;
   uint8_t commandInv = ~command;


   uint32_t data = ((uint32_t)address    << 24) |
                   ((uint32_t)addressInv << 16) |
                   ((uint32_t)command    <<  8) |
                    (uint32_t)commandInv;


   myIRsender.sendNEC(data, 32, 0);
   Serial.println("  Sent end-of-message code (command=0).");
   printNECPulseTrain(data);
   Serial.println();
 }
}

void printNECPulseTrain(uint32_t data) {
 Serial.println("    Theoretical NEC raw pulses [microseconds]:");


 Serial.print("      Mark=");
 Serial.print(MY_NEC_HEADER_MARK);
 Serial.print("us, Space=");
 Serial.print(MY_NEC_HEADER_SPACE);
 Serial.println("us");

 for (int i = 0; i < 32; i++) {
   bool bitValue = (data >> i) & 1;
   unsigned int spaceDuration = bitValue ? MY_NEC_ONE_SPACE : MY_NEC_ZERO_SPACE;


   Serial.print("      Mark=");
   Serial.print(MY_NEC_BIT_MARK);
   Serial.print("us, Space=");
   Serial.print(spaceDuration);
   Serial.println("us");
 }

 Serial.print("      Mark=");
 Serial.print(MY_NEC_TRAILER_MARK);
 Serial.println("us");


 Serial.println("    [End of pulses]");
}
