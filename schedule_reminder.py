import os
import requests
import json
from datetime import datetime, timedelta
import pytz

def load_schedule():
    try:
        with open('schedule.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("⚠️ 警告：未找到 schedule.json")
        return []
    except json.JSONDecodeError:
        print("⚠️ 警告：schedule.json 格式错误")
        return []

def send_schedule_to_wechat(content):
    api_url = "https://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": os.getenv("WXPUSHER_APP_TOKEN"),
        "content": content,
        "summary": "今日课程提醒",
        "contentType": 1,
        "topicIds": [int(os.getenv("WXPUSHER_TOPIC_ID"))]
    }
    
    try:
        response = requests.post(api_url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        print(f" 推送结果：{result}")
        return result["code"] == 1000
    except Exception as e:
        print(f" 发送失败：{str(e)}")
        return False

def get_beijing_time():
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

def send_daily_schedule():
    current_time = get_beijing_time()
    print(f" 北京时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    schedule = load_schedule()
    if not schedule:
        print("⚠️ 没有课程需要提醒")
        return

    today = current_time.date()
    today_weekday = current_time.isoweekday()
    current_week = (current_time.isocalendar()[1] - 1) % 2 + 1
    
    daily_courses = []
    
    for course in schedule:
        print(f"\n 正在检查：{course['course_name']}")
        
        week_type = course.get("week_type", "every").lower()
        week_condition = (
            (week_type == "single" and current_week == 1) or
            (week_type == "double" and current_week == 2) or
            (week_type == "every")
        )
        
        weekday_condition = course["weekday"] == today_weekday
        
        print(f" 匹配条件：周{today_weekday} | 第{current_week}周")
        print(f" 周次条件：{'满足' if week_condition else '不满足'}")
        print(f"️ 星期条件：{'满足' if weekday_condition else '不满足'}")

        if week_condition and weekday_condition:
            try:
                naive_time = datetime.strptime(course['start_time'], "%H:%M")
                start_time = datetime.combine(today, naive_time.time())
                daily_courses.append({
                    "course_name": course['course_name'],
                    "start_time": start_time.strftime('%H:%M'),
                    "location": course['location'],
                    "week_type": week_type
                })
            except ValueError:
                print(f"⛔ 时间格式错误：{course['start_time']}")
                continue
    
    if daily_courses:
        content = " 今日课程提醒：\n"
        for course in daily_courses:
            content += f"课程名称：{course['course_name']}\n"
            content += f" 时间：{course['start_time']}（{course['week_type']}周）\n"
            content += f" 地点：{course['location']}\n\n"
        
        print("\n✅ 今日课程：\n")
        print(content.replace('', '').strip())
        
        if send_schedule_to_wechat(content):
            print(" 提醒发送成功")
        else:
            print("⚠️ 提醒发送失败")
    else:
        print(" 今日没有课程")

if __name__ == "__main__":
    send_daily_schedule()
