#include <Arduino.h>
#include <IRremote.h>

#define IR_RECEIVE_PIN 4
IRrecv myIRreceiver(IR_RECEIVE_PIN);

static const uint8_t BITS_PER_MESSAGE = 32;
static uint8_t bitBuffer[BITS_PER_MESSAGE];
static uint8_t bitCount = 0;

bool firstFrame = true;

void setup() {
  Serial.begin(9600);
  Serial.println("Minimal IR Receiver");
  myIRreceiver.enableIRIn();
}

void loop() {
  if (myIRreceiver.decode()) {
    auto pRawData = myIRreceiver.decodedIRData.rawDataPtr;
    if (pRawData) {
      uint8_t rawLen = pRawData->rawlen;
      IRRawbufType* rawBuf = pRawData->rawbuf;

      const unsigned int TICK_MICROS = 50;

      int index = 0;

      if (rawLen > 0) {
        unsigned int firstPulse = rawBuf[0] * TICK_MICROS;
        if (firstPulse < 100) {
          index = 1; 
        }
      }

      auto decodeBitFromSpace = [&](unsigned int spaceMicros) {
        if (spaceMicros < 1000) return 0;
        else                    return 1;
      };

      bool headerSkipped = false;
      while ((index + 1) < rawLen) {
        unsigned int mark  = rawBuf[index] * TICK_MICROS;
        index++;
        unsigned int space = rawBuf[index] * TICK_MICROS;
        index++;

        if (!headerSkipped && (mark > 2000) && (space > 2000)) {
          headerSkipped = true; 
          continue; 
        }

        uint8_t bitVal = decodeBitFromSpace(space);
        storeBitAndCheck(bitVal);
      }
    }

    myIRreceiver.resume(); 
  }
}

void storeBitAndCheck(uint8_t bitVal) {
  bitBuffer[bitCount++] = bitVal;

  if (bitCount == BITS_PER_MESSAGE) {
    uint32_t data = 0;
    for (int i = 0; i < 32; i++) {
      data |= ((uint32_t)(bitBuffer[i] & 1) << i);
    }

    uint8_t address    = (data >> 24) & 0xFF;
    uint8_t addressInv = (data >> 16) & 0xFF;
    uint8_t command    = (data >>  8) & 0xFF;
    uint8_t commandInv =  data       & 0xFF;

    bitCount = 0;

    if (firstFrame) {
      firstFrame = false;
      return; 
    }

    bool addressOK = (addressInv == (uint8_t)(~address));
    bool commandOK = (commandInv == (uint8_t)(~command));

    if (!addressOK || !commandOK) {
      Serial.println("\nIntegrity check FAILED!");
    } else {
      if (command != 0) {
        Serial.write(command);
      }
    }
  }
}
