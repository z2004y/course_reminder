# course_reminder（课程提醒推送项目）

## 项目介绍

本项目是一个用于每日课程提醒的 Python 脚本，它从 `schedule.json` 文件中读取课程安排，并根据当前日期和时间，通过微信推送平台（例如：WxPusher）向用户发送课程提醒。

## 主要功能

* **读取课程安排：** 从 `schedule.json` 文件中读取课程信息。
* **日期和时间判断：** 根据当前日期、星期几和周次，判断是否有课程需要提醒。
* **微信推送：** 通过微信推送平台，向用户发送 HTML 格式的课程提醒消息，包含课程名称、时间、地点和周次等信息。
* **周次计算：** 根据开学日期，自动计算当前是第几周。
* **周次类型处理：** 支持每周、单周、双周和具体周次列表等多种周次类型。
* **HTML 消息美化：** 使用 HTML 和 CSS 样式，美化微信推送的消息内容。
* **错误处理：** 包含错误处理机制，防止脚本在遇到错误时崩溃。

## 文件结构

```
schedule_reminder/
├── schedule_reminder.py  # 主要的 Python 脚本
├── schedule.json        # 课程安排 JSON 文件
└── README.md            # 项目介绍和使用指南
```

## 使用指南

### 1. 准备工作

* **安装 Python 3.6+：** 确保您的计算机上安装了 Python 3.6 或更高版本。
* **安装依赖库：** 运行以下命令安装所需的 Python 库：

    ```bash
    pip install requests pytz
    ```

* **获取微信推送凭据：** 在微信推送平台（例如：WxPusher）上注册账号，并获取 `appToken` 和 `topicId`。

### 2. 配置课程安排

* 创建 `schedule.json` 文件，并按照以下格式填写课程信息：

    ```json
    [
      {
        "course_name": "综合英语 Ⅳ",
        "start_time": "08:00",
        "location": "知行楼4101",
        "weekday": 1,
        "week_type": "every"
      },
      {
        "course_name": "中国文化概要",
        "start_time": "08:00",
        "location": "知行楼4209",
        "weekday": 2,
        "week_type": "1,3,5,9,11,13,15,17"
      },
      // ... 其他课程
    ]
    ```

    * `course_name`：课程名称。
    * `start_time`：课程开始时间（格式为 "HH:MM"）。
    * `location`：课程地点。
    * `weekday`：星期几（1=周一，2=周二，...，7=周日）。
    * `week_type`：周次类型（"every"：每周，"single"：单周，"double"：双周，或具体的周次列表，例如："1,3,5,7"）。

* 在 `schedule_reminder.py` 脚本中，修改 `start_date_str` 变量，将其设置为您的开学日期（格式为 "YYYY-MM-DD"）。

### 3. 配置微信推送

* 设置环境变量 `WXPUSHER_APP_TOKEN` 和 `WXPUSHER_TOPIC_ID`，将它们设置为您的微信推送凭据。

    * 在 Linux 或 macOS 上，可以使用以下命令：

        ```bash
        export WXPUSHER_APP_TOKEN="your_app_token"
        export WXPUSHER_TOPIC_ID="your_topic_id"
        ```

    * 在 Windows 上，可以使用以下命令：

        ```bash
        set WXPUSHER_APP_TOKEN=your_app_token
        set WXPUSHER_TOPIC_ID=your_topic_id
        ```

### 4. 运行脚本

* 运行 `schedule_reminder.py` 脚本：

    ```bash
    python schedule_reminder.py
    ```

* 脚本将每天早上 6:40 自动运行，并发送课程提醒消息。

### 5. GitHub Actions (可选)

* 可以将此脚本部署到 GitHub Actions，以实现自动化运行。
* 在您的 GitHub 仓库中，创建 `.github/workflows/schedule_reminder.yml` 文件，并添加以下内容：

    ```yaml
    name: Daily Schedule Reminder

    on:
      schedule:
        - cron: '40 22 * * *'  # UTC 时间，换算为北京时间是早上 6:40

    jobs:
      send_reminder:
        runs-on: ubuntu-latest

        steps:
        - name: Checkout code
          uses: actions/checkout@v2

        - name: Set up Python
          uses: actions/setup-python@v2
          with:
            python-version: 3.8

        - name: Install dependencies
          run: pip install requests pytz

        - name: Run schedule reminder
          env:
            WXPUSHER_APP_TOKEN: ${{ secrets.WXPUSHER_APP_TOKEN }}
            WXPUSHER_TOPIC_ID: ${{ secrets.WXPUSHER_TOPIC_ID }}
          run: python schedule_reminder.py
    ```

* 在 GitHub 仓库的 "Settings" -> "Secrets" 中，添加 `WXPUSHER_APP_TOKEN` 和 `WXPUSHER_TOPIC_ID` 这两个 secrets。

### 6. 自定义

* 您可以根据需要修改 `schedule_reminder.py` 脚本，例如：
    * 修改推送时间。
    * 修改消息内容和格式。
    * 添加更多课程信息。
    * 使用其他微信推送平台。

## 注意事项

* 确保 `schedule.json` 文件存在且格式正确。
* 将 `start_date_str` 变量设置为正确的开学日期。
* 确保微信推送凭据设置正确。
* 根据需要修改 HTML 和 CSS 样式，以美化消息内容。
* 如果遇到任何问题，请查看脚本的输出和错误信息。
