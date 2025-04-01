import os
import requests
import json
from datetime import datetime, timedelta
import pytz  # 新增时区库

def load_schedule():
    try:
        with open('schedule.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print("⚠️ 警告：未找到schedule.json")
        return []
    except json.JSONDecodeError:
        print("⚠️ 警告：schedule.json 格式错误")
        return []

def send_schedule_to_wechat(content):
    api_url = "https://wxpusher.zjiecode.com/api/send/message"
    data = {
        "appToken": os.getenv("WXPUSHER_APP_TOKEN"),
        "content": content,
        "summary": "课程提醒",
        "contentType": 1,
        "topicIds": [int(os.getenv("WXPUSHER_TOPIC_ID"))]
    }
    
    try:
        response = requests.post(api_url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        print(f"📤 推送结果：{result}")
        return result["code"] == 1000
    except Exception as e:
        print(f"🔴 发送失败：{str(e)}")
        return False

def get_beijing_time():
    # 获取北京时间
    tz = pytz.timezone('Asia/Shanghai')
    return datetime.now(tz)

def check_and_send_schedule():
    current_time = get_beijing_time()
    print(f"🕒 北京时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    schedule = load_schedule()
    if not schedule:
        print("⚠️ 没有课程需要提醒")
        return

    current_weekday = current_time.isoweekday()  # 1=周一，7=周日
    current_week = (current_time.isocalendar()[1] - 1) % 2 + 1  # 更准确的周次计算
    
    for course in schedule:
        print(f"\n🔍 正在检查：{course['course_name']}")
        
        # 时区处理
        try:
            naive_time = datetime.strptime(course['start_time'], "%H:%M")
            start_time = current_time.replace(
                hour=naive_time.hour,
                minute=naive_time.minute,
                second=0,
                microsecond=0
            )
        except ValueError:
            print(f"⛔ 时间格式错误：{course['start_time']}")
            continue

        # 时间条件判断
        remind_time = start_time - timedelta(minutes=10)
        time_condition = remind_time <= current_time < start_time
        
        # 周类型条件
        week_type = course.get("week_type", "every").lower()
        week_condition = (
            (week_type == "single" and current_week == 1) or
            (week_type == "double" and current_week == 2) or
            (week_type == "every")
        )
        
        # 星期判断
        weekday_condition = course["weekday"] == current_weekday
        
        print(f"⏰ 课程时间：{start_time.strftime('%H:%M')}")
        print(f"📆 匹配条件：周{current_weekday} | 第{current_week}周")
        print(f"⏳ 时间条件：{'满足' if time_condition else '不满足'}")
        print(f"📅 周次条件：{'满足' if week_condition else '不满足'}")
        print(f"🗓️ 星期条件：{'满足' if weekday_condition else '不满足'}")

        if all([time_condition, week_condition, weekday_condition]):
            content = f"""📚 课程提醒：
课程名称：{course['course_name']}
🕐 时间：{start_time.strftime('%H:%M')}（{week_type}周）
📍 地点：{course['location']}
⏳ 还剩：{round((start_time - current_time).total_seconds()/60)}分钟"""
            
            print("\n✅ 触发提醒：")
            print(content.replace('📚', '').strip())
            
            if send_schedule_to_wechat(content):
                print("🎉 提醒发送成功")
            else:
                print("⚠️ 提醒发送失败")

if __name__ == "__main__":
    check_and_send_schedule()