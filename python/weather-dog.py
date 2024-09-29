import urllib.request
import json

# 定义彩云天气 API URL
# 彩云api官网 https://docs.caiyunapp.com/weather-api/
api_key = "填写彩云天气申请的api"
latitude = 39.2072
longitude = 101.6656
url = f"https://api.caiyunapp.com/v2.6/{api_key}/{longitude},{latitude}/daily?dailysteps=2"

# 初始化输出信息变量
output_title = "🌤 未来两天的天气情况 🌤 \n"
output_description = ""
output_content = ""

#初始化通知相关信息
# 自建参考方案：https://github.com/songquanpeng/message-pusher
SERVER = "http://localhost:3000"
USERNAME = "填写自己的用户名称"
TOKEN = "填写自己的通知token"

#发送通知
def send_message(title, description, content,channel):
        url = f"{SERVER}/push/{USERNAME}"
        data = {
            "title": title,
            "description": description,
            "content": content,
            "token": TOKEN,
            "channel": channel
        }

        # 将数据转换为 JSON 格式
        json_data = json.dumps(data).encode('utf-8')

        # 创建请求对象
        req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})

        try:
             # 发送请求并获取响应
            with urllib.request.urlopen(req) as response:
                res_json = json.loads(response.read().decode('utf-8'))

            if res_json.get("success"):
                return None
            else:
                return res_json.get("message", "Unknown error occurred.")

        except urllib.error.HTTPError as e:
            return f"notice :HTTP error occurred: {e.code} - {e.reason}"
        except urllib.error.URLError as e:
            return f"notice :URL error occurred: {e.reason}"
        except Exception as e:
            return f"notice :An unexpected error occurred: {e}"
        print("消息发送成功")



# 发送请求
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())

    # 获取天气数据
    daily_weather = data.get("result", {}).get("daily", {})
    
    if len(daily_weather.get("precipitation", [])) > 1:
        first_day = daily_weather["precipitation"][0]
        second_day = daily_weather["precipitation"][1]
        
        first_day_temp = daily_weather["temperature"][0]
        second_day_temp = daily_weather["temperature"][1]

        # 白天和晚上的降水概率
        second_day_day_precipitation = daily_weather["precipitation_08h_20h"][1]
        second_day_night_precipitation = daily_weather["precipitation_20h_32h"][1]

        rain_today = first_day["probability"] > 0 or second_day_day_precipitation["probability"] > 0 or second_day_night_precipitation["probability"] > 0
        temp_difference = abs(second_day_temp["avg"] - first_day_temp["avg"])

        # 构建输出内容
        output_description += f"**日期**: {first_day['date']} 🗓 \n"
        output_description += f"**白天降水概率**: {first_day['probability']}% 🌧 \n"
        output_description += f"**最高气温**: {first_day_temp['max']}°C, **最低气温**: {first_day_temp['min']}°C \n\n"

        output_description += f"**日期**: {second_day['date']} 🗓\n"
        output_description += f"**白天降水概率**: {second_day_day_precipitation['probability']}% 🌧\n"
        output_description += f"**晚上降水概率**: {second_day_night_precipitation['probability']} 🌙\n"
        output_description += f"**最高气温**: {second_day_temp['max']}°C, **最低气温**: {second_day_temp['min']}°C\n\n"

        # 检查条件并构建内容
        if rain_today or temp_difference > 5:
            msg_des = ''
            output_content += "⚠ **注意事项** ⚠\n"
            if rain_today:
                output_content += "🌧 未来两天可能会下雨，请注意带伞！\n"
                msg_des = f"两天内可能会下雨:{first_day['probability']}% {second_day_day_precipitation['probability']}%"

            if temp_difference > 5:
                output_content += f"🌡 温差超过5度，注意适时增减衣物！当前温差: {temp_difference}°C\n"
                msg_des = f"🌧两天温度变化:{first_day_temp["avg"]}% {second_day_temp["avg"] }%"
            result = ''
            result += output_title;
            result += "\n"
            result += output_description;
            result += output_content;

            send_message("异常天气提醒",msg_des,result,'weixin')
            send_message("异常天气提醒",msg_des,result,'dingding')

            #print(result)

    else:
        output_content += "无法获取天气数据。"

    # 输出结果
    print(output_title)
    print(output_description)
    print(output_content)


except urllib.error.HTTPError as e:
    print(f"HTTP 错误: {e.code}")
except urllib.error.URLError as e:
    print(f"请求失败: {e.reason}")
except Exception as e:
    print(f"发生错误: {e}")
