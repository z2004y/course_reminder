import os
import requests
import json
from datetime import datetime
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
        "contentType": 2,  # 设置 contentType 为 2，表示 HTML 格式
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

def calculate_week(start_date, current_date):
    """计算当前日期是相对于开学日期的第几周"""
    days = (current_date.date() - start_date).days
    return (days // 7) + 1 # 修改为返回实际周数

def send_daily_schedule():
    current_time = get_beijing_time()
    print(f" 北京时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    schedule = load_schedule()
    if not schedule:
        print("⚠️ 没有课程需要提醒")
        return

    today = current_time.date()
    today_weekday = current_time.isoweekday()
    
    # 在代码中指定开学日期
    start_date_str = "2023-09-04"  # 修改为你的开学日期
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"⛔ 开学日期格式错误：{start_date_str}")
        return
    
    current_week = calculate_week(start_date, current_time)
    
    daily_courses = []
    
    for course in schedule:
        print(f"\n 正在检查：{course['course_name']}")
        
        week_type = course.get("week_type", "every").lower()
        
        if week_type == "every":
            week_condition = True
        else:
            try:
                week_list = [int(w) for w in week_type.split(",")]
                week_condition = current_week in week_list
            except ValueError:
                print(f"⛔ 周次类型格式错误：{week_type}")
                week_condition = False
        
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
                    "week_type": course["week_type"] #使用json中的week_type
                })
            except ValueError:
                print(f"⛔ 时间格式错误：{course['start_time']}")
                continue
    
    if daily_courses:
        content = f"""
        <html>
        <head>
        <title>今日课程提醒</title>
        <style>
        body { font-family: sans-serif; }
        h1 { color: #3498db; }
        p { margin-bottom: 10px; }
        strong { font-weight: bold; }
        hr { border: 1px solid #ddd; }
        </style>
        </head>
        <body>
        <h1>今日课程提醒</h1>
        <p><strong>本周是第 {current_week} 周</strong></p>
        """
        for course in daily_courses:
            content += f"<p><strong>课程名称：</strong> {course['course_name']}</p>"
            content += f"<p><strong>时间：</strong> {course['start_time']}（{course['week_type']}）</p>"
            content += f"<p><strong>地点：</strong> {course['location']}</p><hr>"
        content += "</body></html>"
        
        print("\n✅ 今日课程：\n")
        print(content.replace('<html><head><title>今日课程提醒</title></head><body>', '').replace('</body></html>','').strip())
        
        if send_schedule_to_wechat(content):
            print(" 提醒发送成功")
        else:
            print("⚠️ 提醒发送失败")
    else:
        print(" 今日没有课程")

if __name__ == "__main__":
    send_daily_schedule()
