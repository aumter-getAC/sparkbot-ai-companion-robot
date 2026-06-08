/*
 * ESP-IDF 侧接入 AI Bridge 的示例代码片段。
 * 作用：把用户语音识别后的文本 POST 到服务端 /chat，拿到 reply 与 command。
 *
 * 注意：这是核心逻辑片段，不是完整可编译工程。移植到原 SparkBot 工程时，通常放在
 * ai_chat / app_chat / network 相关模块中，并复用项目已有 Wi-Fi、HTTP、JSON、UI、TTS 组件。
 */

#include <stdio.h>
#include <string.h>
#include "esp_http_client.h"
#include "esp_log.h"

#define AI_BRIDGE_URL "http://192.168.1.100:8000/chat"   // 改成你的电脑/服务器 IP

static const char *TAG = "qwen_bridge";

esp_err_t sparkbot_send_text_to_ai_bridge(const char *user_text)
{
    char post_data[1024];
    snprintf(post_data, sizeof(post_data),
             "{\"user_id\":\"sparkbot\",\"message\":\"%s\",\"mode\":\"companion\"}",
             user_text);

    esp_http_client_config_t config = {
        .url = AI_BRIDGE_URL,
        .method = HTTP_METHOD_POST,
        .timeout_ms = 15000,
    };

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (client == NULL) {
        ESP_LOGE(TAG, "Failed to init http client");
        return ESP_FAIL;
    }

    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, post_data, strlen(post_data));

    esp_err_t err = esp_http_client_perform(client);
    if (err == ESP_OK) {
        int status = esp_http_client_get_status_code(client);
        int len = esp_http_client_get_content_length(client);
        ESP_LOGI(TAG, "HTTP status=%d, content_length=%d", status, len);
        // TODO: 读取响应 body，用 cJSON 解析 reply 和 command。
        // reply -> 屏幕显示 + TTS 播放
        // command -> 转发给 ESP32-C3 小车底盘，例如 forward/stop/line_tracking
    } else {
        ESP_LOGE(TAG, "HTTP POST failed: %s", esp_err_to_name(err));
    }

    esp_http_client_cleanup(client);
    return err;
}
