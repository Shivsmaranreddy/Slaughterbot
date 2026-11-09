/* Experimental inert-object gate. NOT COMPILED OR HARDWARE-TESTED.
   D2: normally-closed safety loop to GND, INPUT_PULLUP. Open loop = stop.
   D3: local momentary arm/reset button to GND. D9: servo signal.
   Independent physical stop must also interrupt actuator power.
   Protocol: L/R/H followed by newline, maximum 15 characters.
   Neutral 90 degrees; limits 70..110; step 2 degrees.
*/
#include <Servo.h>
Servo gate;
const byte STOP_PIN=2, ARM_PIN=3, SERVO_PIN=9;
bool armed=false;
bool previousArmLow=true; // Require release then a fresh local press after startup/stop.
int angle=90;
unsigned long lastCommand=0, lastMove=0;
char buffer[16]; byte used=0;
void halt(){ armed=false; gate.detach(); used=0; }
void setup(){
  pinMode(STOP_PIN,INPUT_PULLUP); pinMode(ARM_PIN,INPUT_PULLUP);
  Serial.begin(115200); halt();
}
void loop(){
  bool armLow=digitalRead(ARM_PIN)==LOW;
  bool armPressed=armLow && !previousArmLow;
  previousArmLow=armLow;
  if(digitalRead(STOP_PIN)!=LOW){ halt(); }
  if(!armed && digitalRead(STOP_PIN)==LOW && armPressed){
    // Clear queued host commands before local arming.
    while(Serial.available()) Serial.read();
    angle=90; gate.attach(SERVO_PIN); gate.write(angle);
    armed=true; lastCommand=millis(); Serial.println("ARMED");
  }
  if(armed && millis()-lastCommand>1000){ halt(); Serial.println("TIMEOUT"); }
  while(Serial.available()){
    char c=Serial.read();
    if(c=='\n'){
      buffer[used]=0;
      if(used==1 && buffer[0]=='S'){ halt(); Serial.println("STOPPED"); }
      else if(armed && used==1 && digitalRead(STOP_PIN)==LOW){
        char cmd=buffer[0];
        if(cmd=='H'){ lastCommand=millis(); Serial.println("HELD"); }
        else if((cmd=='L'||cmd=='R') && millis()-lastMove>=100){
          int next=angle+(cmd=='L'?-2:2);
          if(next>=70 && next<=110){angle=next;gate.write(angle);lastMove=millis();lastCommand=millis();Serial.println("OK");}
          else Serial.println("LIMIT");
        } else Serial.println("REJECTED");
      } else Serial.println("REJECTED");
      used=0;
    } else if(c!='\r'){
      if(used>=15){halt();Serial.println("OVERFLOW");}
      else buffer[used++]=c;
    }
  }
}
