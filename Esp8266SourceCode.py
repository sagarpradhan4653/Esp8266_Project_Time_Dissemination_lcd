#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <LiquidCrystal.h>
#include <time.h>
#ifndef STASSID
#define STASSID "SAGAR"
#define STAPSK  "HONEYNINNI"
#endif
#define D0 16 // GPIO3
#define D1 5 // GPIO1
#define D2 4 // GPIO16
#define D3 0 // GPIO5
#define D4 2 // GPIO4
#define D5 14 // GPIO14
#define BUF_LEN 256
char buffer_time[26];
char buffer_date[26];
struct tm* tm_info;

LiquidCrystal lcd(D0, D1, D2, D3, D4, D5);

const char * ssid = STASSID;  const char * pass = STAPSK;
unsigned int localPort = 2390;      

IPAddress timeServerIP; 
const char* ntpServerName = "time.nplindia.org";
const int NTP_PACKET_SIZE = 48;
byte packetBuffer[ NTP_PACKET_SIZE]; 
WiFiUDP udp;

int h = 0; int m = 0; int s = 0; int y = 0; int M = 0;
int offset = -1;

void setup() {
  Serial.begin(115200);
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting to ");
  lcd.setCursor(0, 1);
  lcd.print(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.println("WiFi connected");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.println("NTP Sync...........");
  udp.begin(localPort);
}

int MAX_WAIT = 10, WAIT_SEQ = MAX_WAIT+1;


void loop() {
  //Serial.println(udp_id");
  WiFi.hostByName(ntpServerName, timeServerIP);
  sendNTPpacket(timeServerIP); 
  int cb = udp.parsePacket();
  
  if (!cb) {
    Serial.println("no packet yet");
  }
   else {
    Serial.print("packet received, length=");
    Serial.println(cb);


    if(WAIT_SEQ > MAX_WAIT || tm_info->tm_sec == 59)
    {
      WAIT_SEQ = 1;
      Serial.print("i am called......");
      udp.read(packetBuffer, NTP_PACKET_SIZE);
      unsigned long highWord = word(packetBuffer[40], packetBuffer[41]);
      unsigned long lowWord = word(packetBuffer[42], packetBuffer[43]);
      unsigned long secsSince1900 = highWord << 16 | lowWord;
      Serial.print("Seconds since Jan 1 1900 = ");
      Serial.println(secsSince1900);
      Serial.print("Unix time = ");
      const unsigned long seventyYears = 2208988800UL;
      unsigned long epoch = secsSince1900 - seventyYears+19800+offset;
      time_t date_time;
      date_time = epoch;
      tm_info = localtime(&date_time);
    }
    else
    {
      WAIT_SEQ++;-
      tm_info->tm_sec++;
    }
      
    strftime(buffer_time, 26, "%H:%M:%S", tm_info);
    strftime(buffer_date, 26, "%d/%m/%Y", tm_info);
    lcd.clear();
    lcd.setCursor(0, 0); lcd.print("IST     "+String(buffer_time));
    lcd.setCursor(0, 1); lcd.print("DATE  "+String(buffer_date));
  }

  delay(1000);
}

void sendNTPpacket(IPAddress& address) {
  Serial.println("sending NTP packet...");
  memset(packetBuffer, 0, NTP_PACKET_SIZE);
  packetBuffer[0] = 0b11100011;   
  packetBuffer[1] = 0;     
  packetBuffer[2] = 6;    
  packetBuffer[3] = 0xEC;  
  packetBuffer[12]  = 49;
  packetBuffer[13]  = 0x4E;
  packetBuffer[14]  = 49;
  packetBuffer[15]  = 52;
  udp.beginPacket(address, 123);
  udp.write(packetBuffer, NTP_PACKET_SIZE);
  udp.endPacket();
}