#include <Arduino.h>
#include <IRremoteESP8266.h>
#include <IRsend.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>

// 修改1: 使用更稳定的硬件串口（如果可用）或确保引脚兼容性
// 建议使用RX=13, TX=15 这些SoftwareSerial优化引脚
SoftwareSerial mySerial(13, 15); // RX, TX

const uint16_t kIrLed1 = 14;
const uint16_t kIrLed2 = 12;

IRsend irsend(kIrLed1);
IRsend irsend2(kIrLed2); // 新增：第二个红外发射引脚

ESP8266WiFiMulti WiFiMulti;

const char* ssid = "YourSSID";
const char* password = "YourPassword";

ESP8266WebServer server(80);

// 定义 RawDataInfo 结构体，用于存储 rawData 数组及其相关信息
struct RawDataInfo {
  const uint16_t* data;  // 指向 rawData 数组的指针
  uint16_t length;       // rawData 数组的长度
  uint16_t khz;          // 载波频率（单位：kHz）
};

// 定义 Command 结构体，支持不同类型的数据
struct Command {
  const char* name;      // 命令名称
  union {
    uint32_t value;      // NEC 等信号的值
    RawDataInfo rawInfo; // RawData 的相关信息
  };
  bool isRaw;            // 标记是否为 RawData 类型
};

// 定义多个 rawData 数组
uint16_t rawData[147] = {10154, 5088,  542, 510,  566, 1910,  542, 510,  516, 1932,  566, 486,  564, 1882,  540, 512,  542, 1934,  562, 1886,  562, 488,  538, 514,  538, 514,  538, 1910,  540, 512,  540, 512,  566, 1882,  562, 492,  538, 514,  540, 512,  538, 514,  538, 514,  510, 516,  536, 516,  536, 516,  538, 514,  538, 516,  536, 516,  510, 1936,  538, 516,  536, 514,  538, 1910,  536, 1938,  558, 494,  534, 492,  536, 516,  536, 518,  534, 518,  534, 518,  534, 518,  508, 518,  536, 516,  534, 518,  534, 518,  534, 518,  534, 492,  534, 518,  534, 518,  532, 520,  534, 518,  534, 520,  508, 518,  534, 1942,  532, 520,  532, 520,  506, 520,  532, 1942,  532, 522,  530, 522,  506, 520,  532, 522,  530, 524,  528, 524,  530, 522,  528, 524,  502, 524,  528, 524,  528, 524,  530, 524,  526, 524,  528, 520,  506, 1968,  506, 546,  506};  // TROTEC_3550

uint16_t rawData2[147] = {9976, 5274,  588, 496,  564, 1922,  590, 496,  564, 1922,  590, 496,  562, 1922,  590, 496,  564, 1922,  590, 496,  562, 500,  564, 498,  562, 500,  562, 1922,  590, 496,  564, 500,  562, 500,  560, 500,  562, 500,  562, 500,  562, 500,  562, 500,  562, 500,  560, 500,  560, 500,  562, 498,  562, 500,  562, 500,  560, 1924,  588, 498,  562, 500,  560, 502,  560, 1924,  588, 498,  560, 502,  560, 502,  560, 502,  560, 502,  560, 500,  560, 502,  562, 500,  560, 1924,  588, 500,  562, 498,  562, 500,  564, 498,  564, 498,  564, 498,  562, 500,  558, 504,  558, 504,  558, 1926,  506, 2004,  504, 562,  548, 534,  530, 1954,  502, 2008,  502, 560,  528, 534,  550, 512,  548, 510,  550, 512,  548, 514,  522, 538,  522, 542,  520, 542,  520, 542,  518, 1990,  518, 544,  518, 544,  518, 544,  518, 544,  516, 1990,  520};  // TROTEC_3550

uint16_t rawData3[147] = {10046, 5202,  546, 534,  526, 1984,  528, 534,  526, 1984,  526, 536,  526, 1962,  548, 534,  526, 1982,  526, 1984,  528, 534,  526, 536,  526, 536,  526, 1984,  526, 536,  526, 536,  526, 534,  526, 536,  526, 536,  526, 536,  526, 536,  524, 536,  524, 536,  526, 536,  524, 538,  526, 536,  526, 536,  524, 536,  526, 1966,  544, 536,  524, 538,  524, 538,  524, 1966,  544, 538,  524, 538,  524, 536,  524, 538,  524, 538,  524, 536,  524, 536,  524, 536,  524, 528,  534, 518,  542, 538,  524, 518,  544, 538,  522, 520,  542, 1966,  542, 1966,  544, 538,  502, 540,  544, 1966,  542, 1966,  546, 518,  542, 520,  542, 518,  544, 1964,  544, 516,  544, 518,  546, 516,  546, 516,  548, 514,  548, 514,  550, 512,  550, 512,  528, 534,  530, 532,  532, 1978,  530, 530,  532, 530,  532, 528,  534, 1976,  560, 502,  560};  // TROTEC_3550

uint16_t rawData4[147] = {10024, 5226,  556, 506,  554, 1976,  534, 506,  556, 1976,  532, 508,  552, 1978,  532, 508,  554, 1976,  532, 1976,  532, 510,  552, 508,  552, 510,  552, 1976,  532, 508,  554, 1976,  532, 1976,  532, 510,  552, 510,  552, 508,  554, 508,  552, 512,  550, 510,  550, 510,  552, 508,  552, 510,  552, 510,  552, 1978,  532, 510,  552, 1978,  532, 512,  550, 510,  550, 510,  552, 510,  552, 510,  552, 510,  552, 510,  552, 510,  550, 510,  552, 510,  550, 512,  548, 512,  550, 512,  550, 512,  550, 512,  550, 510,  552, 1960,  548, 1960,  550, 512,  550, 512,  550, 512,  550, 1960,  548, 512,  550, 512,  550, 512,  550, 1960,  548, 512,  548, 514,  550, 512,  526, 536,  550, 510,  526, 536,  526, 536,  542, 518,  530, 532,  556, 504,  560, 502,  588, 472,  594, 468,  600, 1908,  626, 1884,  600, 1908,  598};  // TROTEC_3550

uint16_t rawData5[147] = {10046, 5202,  548, 534,  528, 1982,  528, 534,  528, 1982,  528, 532,  528, 1982,  528, 534,  528, 1982,  528, 1980,  530, 534,  528, 532,  530, 532,  528, 1980,  528, 534,  528, 514,  548, 534,  528, 534,  528, 534,  528, 534,  528, 532,  528, 534,  528, 534,  526, 536,  526, 534,  528, 534,  526, 534,  526, 516,  546, 1964,  546, 516,  546, 514,  546, 536,  528, 1962,  546, 536,  526, 514,  548, 534,  526, 514,  548, 514,  548, 514,  548, 514,  548, 1960,  550, 512,  552, 510,  552, 510,  552, 508,  554, 508,  532, 530,  534, 528,  560, 502,  560, 502,  534, 1976,  534, 1976,  560, 502,  562, 500,  538, 524,  562, 1948,  560, 500,  562, 500,  560, 502,  532, 530,  556, 504,  556, 506,  554, 506,  554, 508,  554, 1956,  552, 508,  528, 534,  526, 1984,  524, 1986,  522, 1986,  520, 1988,  498, 2012,  496};  // TROTEC_3550

uint16_t rawData6[147] = {10050, 5198,  556, 528,  534, 1956,  554, 528,  532, 1958,  552, 508,  554, 1956,  552, 510,  552, 1956,  554, 1956,  554, 508,  552, 1958,  552, 510,  552, 1958,  552, 510,  552, 510,  552, 508,  552, 510,  550, 512,  552, 510,  552, 510,  550, 510,  552, 510,  552, 512,  550, 512,  550, 510,  552, 512,  550, 510,  552, 1958,  552, 512,  550, 510,  552, 512,  550, 1958,  550, 510,  554, 508,  552, 510,  554, 508,  552, 510,  550, 512,  550, 510,  552, 1958,  552, 1958,  552, 512,  552, 508,  554, 508,  552, 510,  552, 508,  530, 532,  530, 532,  528, 534,  526, 534,  504, 2006,  504, 2006,  506, 556,  502, 558,  504, 558,  502, 2008,  502, 2008,  502, 560,  502, 560,  502, 560,  500, 562,  500, 560,  502, 560,  502, 560,  500, 562,  500, 2010,  500, 560,  502, 560,  502, 560,  502, 560,  502, 560,  500, 562,  500};  // TROTEC_3550

uint16_t rawData7[147] = {10048, 5202,  544, 536,  526, 1982,  526, 536,  526, 1984,  526, 536,  526, 1984,  526, 536,  526, 1984,  524, 1984,  526, 536,  526, 1966,  544, 536,  524, 1966,  544, 536,  526, 536,  526, 536,  524, 538,  524, 536,  526, 518,  544, 538,  524, 536,  524, 536,  526, 536,  526, 536,  526, 536,  524, 538,  524, 538,  524, 1966,  544, 538,  526, 536,  526, 536,  526, 1984,  524, 538,  524, 538,  524, 538,  524, 538,  526, 534,  524, 520,  544, 1984,  502, 560,  524, 1966,  544, 538,  524, 538,  524, 538,  524, 538,  524, 538,  524, 538,  522, 540,  522, 520,  518, 562,  524, 1966,  544, 1966,  544, 518,  542, 520,  544, 518,  542, 1966,  544, 1966,  546, 516,  546, 514,  548, 514,  548, 512,  550, 512,  526, 536,  528, 532,  528, 532,  530, 1980,  556, 504,  558, 504,  534, 528,  560, 500,  560, 502,  562, 1948,  562};  // TROTEC_3550

uint16_t rawData8[147] = {10050, 5198,  570, 514,  534, 1956,  580, 500,  558, 1952,  534, 528,  558, 1930,  578, 504,  560, 1930,  580, 1930,  554, 528,  558, 484,  554, 526,  534, 1956,  578, 504,  534, 508,  552, 530,  532, 528,  534, 528,  534, 528,  534, 528,  540, 522,  532, 510,  550, 530,  534, 528,  532, 530,  532, 508,  554, 526,  532, 1956,  554, 510,  552, 528,  532, 528,  532, 1958,  552, 530,  532, 528,  534, 510,  550, 530,  532, 530,  532, 510,  552, 530,  530, 510,  552, 1978,  532, 510,  550, 510,  552, 510,  552, 510,  550, 510,  552, 510,  550, 510,  550, 512,  550, 510,  554, 1956,  552, 1960,  552, 508,  552, 510,  552, 510,  550, 1958,  552, 508,  552, 510,  550, 510,  554, 508,  552, 508,  554, 508,  556, 506,  554, 508,  532, 1978,  530, 532,  530, 532,  528, 1982,  504, 2006,  502, 2006,  504, 2006,  502, 2006,  502};  // TROTEC_3550

uint16_t rawData9[147] = {10050, 5202,  544, 518,  544, 1984,  526, 536,  524, 1984,  524, 538,  526, 1984,  526, 1984,  526, 1984,  524, 1984,  526, 518,  544, 536,  524, 536,  526, 1984,  524, 538,  524, 538,  524, 538,  524, 536,  524, 538,  524, 518,  544, 538,  524, 518,  544, 538,  524, 538,  524, 538,  524, 538,  524, 538,  524, 538,  522, 1986,  524, 538,  522, 520,  544, 518,  542, 1988,  522, 520,  518, 544,  518, 544,  542, 540,  498, 542,  532, 530,  518, 544,  518, 542,  544, 1966,  526, 534,  522, 540,  520, 542,  522, 540,  522, 538,  524, 540,  548, 514,  550, 512,  526, 536,  528, 1982,  554, 1958,  556, 504,  560, 502,  584, 1926,  586, 1922,  592, 470,  616, 446,  590, 472,  588, 472,  588, 474,  584, 476,  582, 480,  556, 506,  554, 1956,  552, 510,  550, 1960,  548, 512,  548, 512,  548, 514,  546, 516,  522, 1988,  520};  // TROTEC_3550

                         
// Example of data captured by IRrecvDumpV2.ino
// 定义字典，包含多个命令及其对应的数据
Command dict_cmd[] = {
  {"ear_phone_switcher",  {.value = 0xFFA25D}, false},  // 耳机开关
  {"ear_phone_mute",  {.value = 0xFFE21D}, false}, //  耳机静音
  {"light_up", {.value = 0x807F807F}, false},    //  灯光调亮 
  {"light_down", {.value = 0x807F40BF}, false}, //  灯光调暗
  {"light_countdown_5m", {.value = 0x807FE01F}, false}, //灯光定时5分钟
  {"light_countdown_30m", {.value = 0x807F609F}, false}, //灯光定时30分钟
  {"air_open", {.rawInfo = {rawData, 147, 38}}, true},     // 空调开启制冷
  {"air_close", {.rawInfo = {rawData2, 147, 38}}, true}, // 空调关闭
  {"air_direction_down", {.rawInfo = {rawData3, 147, 38}}, true}, //  空调风向
  {"air_cool", {.rawInfo = {rawData4, 147, 38}}, true}, // 空调制冷
  {"air_wind", {.rawInfo = {rawData5, 147, 38}}, true},//  空调送风
  {"air_countdown_30m", {.rawInfo = {rawData6, 147, 38}}, true}, //  空调定时30分钟
  {"air_countdown_1h", {.rawInfo = {rawData7, 147, 38}}, true},// 空调定时1小时
  {"air_countdown_cancel", {.rawInfo = {rawData8, 147, 38}}, true},//  空调定时取消
  {"air_speed", {.rawInfo = {rawData9, 147, 38}}, true},//  空调风速
  {"tv_boot", {.value = 0xFD48B7}, false}, //  电视开机
  {"tv_vol_up", {.value = 0xFD18E7}, false}, //  电视音量加
  {"tv_vol_down", {.value = 0xFD38C7}, false}, //  电视音量减
  {"tv_mute", {.value = 0xFFE21D7}, false}//  电视静音
};

void sendHttpGet(String cmd) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;              // 新增WiFiClient实例
    HTTPClient http;
    String url = "http://192.168.1.109:8083/" + cmd;
    Serial.println(url);
    http.begin(client, url);        // 修改为带client参数的版本
    http.GET();      // 发送GET请求
    //需要打印HTTP响应码

    http.end();      // 关闭连接
  }
}


void handleAudio(String wd) {
  if (wd.startsWith("web_")) {
    String subCmd = wd.substring(4);  // 提取 "web_" 后续内容
    sendHttpGet(subCmd);             // 调用 HTTP 请求函数
    return;                          // 结束函数执行
  }

  bool found = false;

  for (auto& cmd : dict_cmd) {
    if (wd == cmd.name) {
      found = true;
      if (cmd.isRaw) {
        Serial.println("Executing raw data signal");
        irsend.sendRaw(cmd.rawInfo.data, cmd.rawInfo.length, cmd.rawInfo.khz);
        irsend2.sendRaw(cmd.rawInfo.data, cmd.rawInfo.length, cmd.rawInfo.khz); // 新增
      } else {
        Serial.println("Executing NEC signal");
        irsend.sendNEC(cmd.value);
        irsend2.sendNEC(cmd.value); // 新增
      }
      break;
    }
  }

  if (!found) {
    Serial.println("Invalid wd parameter");
  }
}

void handleCmd() {
  String wd = server.arg("wd");
  bool found = false;

  for (auto& cmd : dict_cmd) {
    if (wd == cmd.name) {
      found = true;
      if (cmd.isRaw) {
        Serial.println("Executing raw data signal");
        irsend.sendRaw(cmd.rawInfo.data, cmd.rawInfo.length, cmd.rawInfo.khz);
        irsend2.sendRaw(cmd.rawInfo.data, cmd.rawInfo.length, cmd.rawInfo.khz); // 新增
      } else {
        Serial.println("Executing NEC signal");
        irsend.sendNEC(cmd.value);
        irsend2.sendNEC(cmd.value); // 新增
      }
      break;
    }
  }

  if (!found) {
    Serial.println("Invalid wd parameter");
  }

  server.send(200, "text/plain", "Command executed");
}

void setup() {
  irsend.begin();
  irsend2.begin(); // 新增：初始化第二个红外发射器
  
  // 修改2: 增加串口调试信息
  Serial.begin(115200);
  Serial.println("Starting serial communication...");
  
  // 修改3: 使用更常见的9600波特率，或根据ASR Pro实际波特率调整
  mySerial.begin(9600);
  Serial.print("Serial baud rate set to: ");
  Serial.println(9600);

  WiFi.mode(WIFI_STA);
  
  WiFiMulti.addAP(ssid, password);

  Serial.println("Connecting to WiFi...");
  while (WiFiMulti.run() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/cmd", HTTP_GET, handleCmd);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();

  /* 新增4: 添加串口数据接收调试
  if (mySerial.available()) {
    String received = mySerial.readStringUntil('\n'); // 添加结束符检测
    Serial.print("Received from ASR Pro: ");
    Serial.println(received);
    handleAudio(received);
  } else {
    // Serial.print(".");  // 可选：用于观察循环状态
  }
  delay(50);
  */

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, attempting to reconnect...");
    while (WiFiMulti.run() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi reconnected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }

  /* 新增5: 增加简单的测试指令发送
  static unsigned long testTimer = 0;
  if (millis() - testTimer > 10000) {
    testTimer = millis();
    Serial.println("Sending test command to ASR Pro...");
    mySerial.println("TEST_CMD");
  }
}
  */
