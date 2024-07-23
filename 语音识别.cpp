#include "asr.h"
#include "setup.h"
#include "myLib/asr_dhtxx.h"
#include "SoftwareSerial.h"
#include "HardwareSerial.h"
#include "myLib/asr_event.h"
#include "myLib/luxiaoban.h"

uint32_t snid;
uint8_t temp;
uint8_t hum;
SoftwareSerial mySerial1(6,5);
uint8_t Txbyte = 0;
uint8_t Rxbyte = 0;
uint8_t Txok = 0;
uint16_t dn = 0;

//{ID:250,keyword:"�����",ASR:"�������",ASRTO:"�������������"}
//{ID:251,keyword:"�����",ASR:"�е�����",ASRTO:"�����������е�"}
//{ID:252,keyword:"�����",ASR:"��С����",ASRTO:"������������С"}
//{speak:����-�����ͷ�,vol:20,speed:10}
//{playid:10001,voice:��ӭʹ�ú��˳��ڷ���������С��С�ͻ����ң������ö������������ң���������������ģʽ}
//{playid:10002,voice:�������ˣ���С��С�ͻ��������������}
DHTxx asr_dht_0(0, DHT11);
void ASR_CODE()
{
  //{ID:500,keyword:"���Ѵ�",ASR:"����ҽ�����Ҫ��ɶ",ASRTO:"��զ֪�������������һ��"}
  if(snid == 500){

  }
  //{ID:501,keyword:"���Ѵ�",ASR:"��˵�˶���",ASRTO:"�ã����¿�Ѱ��"}
  if(snid == 501){

  }
  //{ID:502,keyword:"���Ѵ�",ASR:"����������Ҵ���",ASRTO:"������������ˣ�����������Ķ���"}
  if(snid == 502){

  }
  //{ID:503,keyword:"���Ѵ�",ASR:"��������",ASRTO:"զ�֣�����"}
  if(snid == 503){

  }
  //{ID:504,keyword:"���Ѵ�",ASR:"һ��һ���ڼ�",ASRTO:"���ڶ�ô�����Ҫ��"}
  if(snid == 504){

  }
  //{ID:505,keyword:"���Ѵ�",ASR:"С��ͬѧ",ASRTO:"����"}
  if(snid == 505){

  }
  //{ID:506,keyword:"�����",ASR:"��ǰ�¶�",ASRTO:""}
  if(snid == 506){
    // �ظ�����Ϊ
    temp = asr_dht_0.read_temperature(0);
    play_num((int64_t)(temp * 100), 1);
    Serial.write(temp);
  }
  //{ID:507,keyword:"���Ѵ�",ASR:"С��С��",ASRTO:"��Ը�"}
  if(snid == 507){
    if(Txok == 0){
      Txbyte = 0x20;
      Txok = 1;
      mySerial1.write(Txbyte);
    }
  }
  //{ID:508,keyword:"���Ѵ�",ASR:"���С��",ASRTO:"����"}
  if(snid == 508){

  }
  //{ID:509,keyword:"�����",ASR:"��ǰʪ��",ASRTO:""}
  if(snid == 509){
    // �ظ�����Ϊ��
    hum = asr_dht_0.readHumidity();
    play_num((int64_t)(hum * 100), 1);
    Serial.write(hum);
  }
  //{ID:510,keyword:"�����",ASR:"�򿪵ƹ�",ASRTO:"�ƹ��Ѵ�"}
  if(snid == 510){
    luxiaoban_set_pwm(1,(1000),(50));
    Serial.print("6");
    if(Txok == 0){
      Txbyte = 0x21;
      Txok = 1;
      mySerial1.write(Txbyte);
    }
  }
  //{ID:511,keyword:"�����",ASR:"�����ƹ�",ASRTO:"�ƹ�������Ϊ��������"}
  if(snid == 511){
    luxiaoban_set_pwm(1,(1000),(25));
    Serial.print("1");
  }
  //{ID:512,keyword:"�����",ASR:"�����ƹ�",ASRTO:"�ƹ�������Ϊ�м�����"}
  if(snid == 512){
    luxiaoban_set_pwm(1,(1000),(75));
    Serial.print("2");
  }
  //{ID:513,keyword:"�����",ASR:"�ƹ��������",ASRTO:"�ƹ�������Ϊ�߼�����"}
  if(snid == 513){
    luxiaoban_digital_write(1,1);
    Serial.print("3");
  }
  //{ID:514,keyword:"�����",ASR:"�رյƹ�",ASRTO:"�ƹ��ѹر�"}
  if(snid == 514){
    if(Txok == 0){
      Txbyte = 0x22;
      Txok = 1;
      mySerial1.write(Txbyte);
    }
    luxiaoban_digital_write(1,0);
    Serial.print("9");
  }
}

void setup()
{
  mySerial1.begin(9600);
  Serial.begin(9600);
  asr_dht_0.init();
  mySerial1.setTimeout(10);

  //{ID:84,keyword:"�����",ASR:"��ˣ��",ASRTO:"��"}
  //{ID:85,keyword:"�����",ASR:"�ٽ�˼",ASRTO:"һ"}
  //{ID:86,keyword:"�����",ASR:"ʹ����",ASRTO:"��"}
  //{ID:87,keyword:"�����",ASR:"��˿��",ASRTO:"��"}
  //{ID:88,keyword:"�����",ASR:"������",ASRTO:"��"}
  //{ID:89,keyword:"�����",ASR:"������",ASRTO:"��"}
  //{ID:90,keyword:"�����",ASR:"�ô���",ASRTO:"��"}
  //{ID:91,keyword:"�����",ASR:"��Ȥ��",ASRTO:"��"}
  //{ID:92,keyword:"�����",ASR:"��ů��",ASRTO:"��"}
  //{ID:93,keyword:"�����",ASR:"���͵�",ASRTO:"��"}
  //{ID:94,keyword:"�����",ASR:"������",ASRTO:"ʮ"}
  //{ID:95,keyword:"�����",ASR:"ȼ�ǽ�",ASRTO:"��"}
  //{ID:96,keyword:"�����",ASR:"��פ��",ASRTO:"ǧ"}
  //{ID:97,keyword:"�����",ASR:"��ǹ��",ASRTO:"��"}
  //{ID:98,keyword:"�����",ASR:"�ҷ߰�",ASRTO:"��"}
  //{ID:99,keyword:"�����",ASR:"������",ASRTO:"��"}
  //{ID:100,keyword:"�����",ASR:"����¡",ASRTO:"��"}
}

