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

//{ID:250,keyword:"命令词",ASR:"最大音量",ASRTO:"音量调整到最大"}
//{ID:251,keyword:"命令词",ASR:"中等音量",ASRTO:"音量调整到中等"}
//{ID:252,keyword:"命令词",ASR:"最小音量",ASRTO:"音量调整到最小"}
//{speak:橙子-甜美客服,vol:20,speed:10}
//{playid:10001,voice:欢迎使用好运常在服务器，用小巴小巴唤醒我，或者用二蛋二蛋唤醒我，开启陕西话尬聊模式}
//{playid:10002,voice:我退下了，用小巴小巴或二蛋二蛋唤醒我}
DHTxx asr_dht_0(0, DHT11);
void ASR_CODE()
{
  //{ID:500,keyword:"唤醒词",ASR:"你猜我接下来要干啥",ASRTO:"额咋知道，耐你给额奢一哈"}
  if(snid == 500){

  }
  //{ID:501,keyword:"唤醒词",ASR:"不说了二蛋",ASRTO:"好，有事可寻额"}
  if(snid == 501){

  }
  //{ID:502,keyword:"唤醒词",ASR:"你聪明还是我聪明",ASRTO:"你是最聪明的人，我是最聪明的二蛋"}
  if(snid == 502){

  }
  //{ID:503,keyword:"唤醒词",ASR:"二蛋二蛋",ASRTO:"咋咧，额在"}
  if(snid == 503){

  }
  //{ID:504,keyword:"唤醒词",ASR:"一加一等于几",ASRTO:"等于二么，这哈要问"}
  if(snid == 504){

  }
  //{ID:505,keyword:"唤醒词",ASR:"小巴同学",ASRTO:"我在"}
  if(snid == 505){

  }
  //{ID:506,keyword:"命令词",ASR:"当前温度",ASRTO:""}
  if(snid == 506){
    // 回复可以为
    temp = asr_dht_0.read_temperature(0);
    play_num((int64_t)(temp * 100), 1);
    Serial.write(temp);
  }
  //{ID:507,keyword:"唤醒词",ASR:"小巴小巴",ASRTO:"请吩咐"}
  if(snid == 507){
    if(Txok == 0){
      Txbyte = 0x20;
      Txok = 1;
      mySerial1.write(Txbyte);
    }
  }
  //{ID:508,keyword:"唤醒词",ASR:"你好小巴",ASRTO:"在呢"}
  if(snid == 508){

  }
  //{ID:509,keyword:"命令词",ASR:"当前湿度",ASRTO:""}
  if(snid == 509){
    // 回复可以为空
    hum = asr_dht_0.readHumidity();
    play_num((int64_t)(hum * 100), 1);
    Serial.write(hum);
  }
  //{ID:510,keyword:"命令词",ASR:"打开灯光",ASRTO:"灯光已打开"}
  if(snid == 510){
    luxiaoban_set_pwm(1,(1000),(50));
    Serial.print("6");
    if(Txok == 0){
      Txbyte = 0x21;
      Txok = 1;
      mySerial1.write(Txbyte);
    }
  }
  //{ID:511,keyword:"命令词",ASR:"调暗灯光",ASRTO:"灯光已设置为初级亮度"}
  if(snid == 511){
    luxiaoban_set_pwm(1,(1000),(25));
    Serial.print("1");
  }
  //{ID:512,keyword:"命令词",ASR:"调亮灯光",ASRTO:"灯光已设置为中级亮度"}
  if(snid == 512){
    luxiaoban_set_pwm(1,(1000),(75));
    Serial.print("2");
  }
  //{ID:513,keyword:"命令词",ASR:"灯光调到最亮",ASRTO:"灯光已设置为高级亮度"}
  if(snid == 513){
    luxiaoban_digital_write(1,1);
    Serial.print("3");
  }
  //{ID:514,keyword:"命令词",ASR:"关闭灯光",ASRTO:"灯光已关闭"}
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

  //{ID:84,keyword:"命令词",ASR:"条耍改",ASRTO:"零"}
  //{ID:85,keyword:"命令词",ASR:"官接思",ASRTO:"一"}
  //{ID:86,keyword:"命令词",ASR:"痛官松",ASRTO:"二"}
  //{ID:87,keyword:"命令词",ASR:"削丝误",ASRTO:"三"}
  //{ID:88,keyword:"命令词",ASR:"景粮载",ASRTO:"四"}
  //{ID:89,keyword:"命令词",ASR:"博菌避",ASRTO:"五"}
  //{ID:90,keyword:"命令词",ASR:"裁纯碉",ASRTO:"六"}
  //{ID:91,keyword:"命令词",ASR:"插趣悟",ASRTO:"七"}
  //{ID:92,keyword:"命令词",ASR:"辞暖慌",ASRTO:"八"}
  //{ID:93,keyword:"命令词",ASR:"纵猛淡",ASRTO:"九"}
  //{ID:94,keyword:"命令词",ASR:"锦耗暂",ASRTO:"十"}
  //{ID:95,keyword:"命令词",ASR:"燃智截",ASRTO:"百"}
  //{ID:96,keyword:"命令词",ASR:"佛驻延",ASRTO:"千"}
  //{ID:97,keyword:"命令词",ASR:"隔枪绍",ASRTO:"万"}
  //{ID:98,keyword:"命令词",ASR:"惨愤昂",ASRTO:"亿"}
  //{ID:99,keyword:"命令词",ASR:"丙迈扯",ASRTO:"负"}
  //{ID:100,keyword:"命令词",ASR:"铸猜隆",ASRTO:"点"}
}

