#include "BluetoothSerial.h"
#include <BleKeyboard.h>
#include "esp_bt.h"           // 蓝牙功率控制
#include "esp_pm.h"           // 电源管理
#include "esp_wifi.h"         // WiFi控制（可选）

#ifdef ESP32

// 创建BLE键盘实例
BleKeyboard bleKeyboard("机械键盘BE", "ESP32", 100);

// 定义引脚
const int PIN_A = 14;      // B (Volume Down)
const int PIN_B = 13;      // C (Volume Up)
const int PIN_C = 12;      // 左 12开机连接会报错！
const int PIN_D = 16;      // 右
const int PIN_M = 17;      // 按钮 (Mute/Unmute)D
const int LED_PIN = 2;     // 板载LED (ESP32通常是GPIO2)

// 按键状态变量
bool lastStateA = HIGH;
bool lastStateB = HIGH;
bool lastStateC = HIGH;
bool lastStateD = HIGH;
bool lastStateM = HIGH;

bool currentStateA = HIGH;
bool currentStateB = HIGH;
bool currentStateC = HIGH;
bool currentStateD = HIGH;
bool currentStateM = HIGH;

// 防抖动时间变量
unsigned long lastDebounceTimeA = 0;
unsigned long lastDebounceTimeB = 0;
unsigned long lastDebounceTimeC = 0;
unsigned long lastDebounceTimeD = 0;
unsigned long lastDebounceTimeM = 0;
const unsigned long debounceDelay = 50;

// 音量键长按重复发送
unsigned long lastVolumeRepeatTime = 0;
const unsigned long volumeRepeatDelay = 150;  // 每150ms重复发送一次

// LED闪烁控制
unsigned long lastLedToggleTime = 0;
const unsigned long ledBlinkInterval = 500;  // 闪烁间隔500ms
bool ledState = LOW;

// 蓝牙连接状态
bool wasConnected = false;

void setup() {
  Serial.begin(115200);
  Serial.println("=== ESP32 BLE Keyboard Initializing ===");

  // 初始化引脚为输入并启用内部上拉电阻
  pinMode(PIN_A, INPUT_PULLUP);
  pinMode(PIN_B, INPUT_PULLUP);
  pinMode(PIN_C, INPUT_PULLUP);
  pinMode(PIN_D, INPUT_PULLUP);
  pinMode(PIN_M, INPUT_PULLUP);
  
  // 初始化LED引脚
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // ========== 蓝牙功率优化配置 ==========
  
  // 1. 设置蓝牙发射功率
  // 功率级别说明：
  // - N表示Negative（负数），如ESP_PWR_LVL_N0至N9，对应0dBm至-9dBm
  // - P表示Positive（正数），如ESP_PWR_LVL_P1至P9，对应+1dBm至+9dBm
  // 功率范围：ESP_PWR_LVL_N9 (-9dBm) 到 ESP_PWR_LVL_P9 (+9dBm)，共19级
  
  // 原代码（最大功率）：
  // esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_DEFAULT, ESP_PWR_LVL_P9);  // +9dBm
  // esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, ESP_PWR_LVL_P9);      // 广播功率
  // esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_SCAN, ESP_PWR_LVL_P9);     // 扫描功率
  // Serial.println("[CONFIG] BLE TX Power: +9dBm (MAX)");
  
  // 修改为默认功率设置
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_DEFAULT, ESP_PWR_LVL_N0);  // 默认功率 (0dBm)
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_ADV, ESP_PWR_LVL_N0);      // 广播功率
  esp_ble_tx_power_set(ESP_BLE_PWR_TYPE_SCAN, ESP_PWR_LVL_N0);     // 扫描功率
  Serial.println("[CONFIG] BLE TX Power: 0dBm (Default)");

  // 2. 初始化BLE键盘
  bleKeyboard.begin();
  Serial.println("[BLE] Keyboard started: 机械键盘BE");

  // 3. 禁止蓝牙休眠 + 锁定CPU频率
  esp_pm_config_esp32_t pm_config;
  pm_config.max_freq_mhz = 240;
  pm_config.min_freq_mhz = 240;          // 不降频，保持240MHz
  pm_config.light_sleep_enable = false;  // 禁用轻度睡眠
  
  esp_err_t err = esp_pm_configure(&pm_config);
  if (err == ESP_OK) {
    Serial.println("[CONFIG] Power Management: Sleep DISABLED, CPU@240MHz");
  } else {
    Serial.printf("[WARNING] PM config failed: %d\n", err);
  }

  // 4. 可选：禁用WiFi协处理器（避免干扰）
  // 如果不需要WiFi，取消下面注释
  esp_wifi_stop();
  Serial.println("[CONFIG] WiFi disabled");
  
  Serial.println("[STATUS] Waiting for Bluetooth connection...");
  Serial.println("=========================================");
}

void loop() {
  // 检查蓝牙连接状态并控制LED
  bool isConnected = bleKeyboard.isConnected();
  
  if (isConnected) {
    // 连接状态：LED常亮
    digitalWrite(LED_PIN, HIGH);
    
    // 检测到新连接
    if (!wasConnected) {
      Serial.println("✓ Bluetooth Connected!");
      wasConnected = true;
    }
    
    // 读取按键状态
    bool readingA = digitalRead(PIN_A);
    bool readingB = digitalRead(PIN_B);
    bool readingC = digitalRead(PIN_C);
    bool readingD = digitalRead(PIN_D);
    bool readingM = digitalRead(PIN_M);

    // ========== A键：音量减（支持长按） ==========
    if (readingA != lastStateA) {
      lastDebounceTimeA = millis();
    }

    if ((millis() - lastDebounceTimeA) > debounceDelay) {
      if (readingA != currentStateA) {
        currentStateA = readingA;
        if (currentStateA == LOW) {  // 按下
          bleKeyboard.write(KEY_MEDIA_VOLUME_DOWN);
          Serial.println("Volume Down");
          lastVolumeRepeatTime = millis();
        }
      }
    }
    
    // 长按重复发送音量减
    if (currentStateA == LOW && (millis() - lastVolumeRepeatTime) > volumeRepeatDelay) {
      bleKeyboard.write(KEY_MEDIA_VOLUME_DOWN);
      Serial.println("Volume Down (repeat)");
      lastVolumeRepeatTime = millis();
    }
    
    lastStateA = readingA;

    // ========== B键：音量加（支持长按） ==========
    if (readingB != lastStateB) {
      lastDebounceTimeB = millis();
    }

    if ((millis() - lastDebounceTimeB) > debounceDelay) {
      if (readingB != currentStateB) {
        currentStateB = readingB;
        if (currentStateB == LOW) {  // 按下
          bleKeyboard.write(KEY_MEDIA_VOLUME_UP);
          Serial.println("Volume Up");
          lastVolumeRepeatTime = millis();
        }
      }
    }
    
    // 长按重复发送音量加
    if (currentStateB == LOW && (millis() - lastVolumeRepeatTime) > volumeRepeatDelay) {
      bleKeyboard.write(KEY_MEDIA_VOLUME_UP);
      Serial.println("Volume Up (repeat)");
      lastVolumeRepeatTime = millis();
    }
    
    lastStateB = readingB;

    // ========== M键：静音 ==========
    if (readingM != lastStateM) {
      lastDebounceTimeM = millis();
    }

    if ((millis() - lastDebounceTimeM) > debounceDelay) {
      if (readingM != currentStateM) {
        currentStateM = readingM;
        if (currentStateM == LOW) {  // 按下时触发
          bleKeyboard.write(KEY_MEDIA_MUTE);
          Serial.println("Mute/Unmute");
        }
      }
    }
    lastStateM = readingM;

    // ========== C键：左方向键 ==========
    if (readingC != lastStateC) {
      lastDebounceTimeC = millis();
    }

    if ((millis() - lastDebounceTimeC) > debounceDelay) {
      if (readingC != currentStateC) {
        currentStateC = readingC;
        if (currentStateC == LOW) {
          bleKeyboard.write(KEY_LEFT_ARROW);
          Serial.println("Left Arrow");
        }
      }
    }
    lastStateC = readingC;

    // ========== D键：右方向键 ==========
    if (readingD != lastStateD) {
      lastDebounceTimeD = millis();
    }

    if ((millis() - lastDebounceTimeD) > debounceDelay) {
      if (readingD != currentStateD) {
        currentStateD = readingD;
        if (currentStateD == LOW) {
          bleKeyboard.write(KEY_RIGHT_ARROW);
          Serial.println("Right Arrow");
        }
      }
    }
    lastStateD = readingD;

  } else {
    // 未连接状态：LED闪烁
    if (millis() - lastLedToggleTime > ledBlinkInterval) {
      ledState = !ledState;
      digitalWrite(LED_PIN, ledState);
      lastLedToggleTime = millis();
    }
    
    // 检测到断开连接
    if (wasConnected) {
      Serial.println("✗ Bluetooth Disconnected! Waiting for reconnection...");
      wasConnected = false;
    }
  }

  delay(10);
}

#else
void setup() {
  Serial.begin(115200);
  Serial.println("This sketch is designed for ESP32.");
}
void loop() {}
#endif
