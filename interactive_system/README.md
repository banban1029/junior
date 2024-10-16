<div align="center">

[![Tour Reservations](https://img.shields.io/badge/Tours-Reservation-orange)](https://yourlink.com)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
[![Flask](https://img.shields.io/badge/Flask-v2.0.2-blue)](https://palletsprojects.com/p/flask/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://www.python.org/)

[![Dialogue Flow](https://img.shields.io/badge/DialogueFlow-v2-blue)](https://dialogflow.cloud.google.com/)
[![Heroku](https://img.shields.io/badge/Heroku-Deployed-blueviolet)](https://www.heroku.com/)
[![Git](https://img.shields.io/badge/Git-Repository-orange)](https://git-scm.com/)

# Tour Reservation System (`旅行対話システム`)

**A Flask-based web application for booking and managing tour reservations.**

This system allows users to choose from three exciting tour options: **温泉ツアー**, **遊園地ツアー**, and **バスツアー**. Each tour has specific rules for availability and pricing.

</div>

## 🚶‍♂️ **Tour Options & Reservation Rules**

### 1. **温泉ツアー**

- **Available Locations**:
  - 登別
  - 有馬
  - 別府
  - 草津
  - 白浜

- **Reservation Rules**:
  - **April**: Reservations are **unavailable** for all locations.
  - **Saturdays**: Afternoon (PM) slots are typically fully booked.

---

### 2. **遊園地ツアー**

- **Available Locations**:
  - USJ 
  - ディズニーランド
  - ディズニーシー
  - 花やしき
  - ひらかたパーク

- **Reservation Rules**:
  - **March 15 - March 31**: Reservations are **unavailable** for all locations.
  - **Weekends**: Higher likelihood of full bookings.
  - **Crowded Locations**: USJ, ディズニーランド, and ディズニーシー have a **higher booking rate**.

---

### 3. **バスツアー**

- **Available Locations**:
  - 中華街 
  - 黒潮市場 
  - 姫路城 
  - ディズニーランド
  - 有馬

- **Reservation Rules**:
  - **Weekday Mornings**: No reservations available.
  - **Booking Rate**: Weekdays and weekends have a **lower booking rate** overall.

---


## 🛠️ **Features**

- 📅 **Dynamic Booking**: The system randomly generates booked slots to simulate real-world availability.
- 📈 **Booking Rates**: Different activities and locations have varying booking rates based on popularity and day of the week.
- ✅ **Validation**: Ensures users can only book valid locations and dates.
- 💰 **Pricing**: Dynamic pricing is implemented for each location based on predefined budget data.
- 🔍 **User-Friendly Interface**: Intuitive design for easy navigation and booking.
- 💗 **Hospitality-Focused Design**: The system is built with a warm and welcoming approach, ensuring that users feel valued and supported throughout the booking process, enhancing their overall experience.


## 📅 **Schedule Format:**

The system uses a schedule format (`schedule.txt`) to display booking availability and reserved slots.

Example for **温泉ツアー** at **登別**:

```plaintext
アクティビティ: 温泉ツアー
========================================
場所: 登別
------------------------------
予約済みスロット:
  日付: 2022/03/05, 時間帯: PM
  日付: 2022/03/12, 時間帯: PM
  日付: 2022/03/19, 時間帯: PM
  日付: 2022/03/26, 時間帯: PM

予約可能スロット:
  日付: 2022/03/01, 時間帯: AM
  日付: 2022/03/01, 時間帯: PM
  日付: 2022/03/02, 時間帯: AM
  日付: 2022/03/02, 時間帯: PM
  ...
  日付: 2022/03/05, 時間帯: AM
  日付: 2022/03/12, 時間帯: AM
  日付: 2022/03/19, 時間帯: AM
  日付: 2022/03/26, 時間帯: AM
==============================
```


## 📜 **License**

Nothing


## ✨ **System Overview**

This experiment uses a **Webhook** to handle POST requests triggered by specific events. The system includes a web server that processes these requests. The **POST request** is a type of HTTP communication where the client (such as a web browser) sends data to the web server.

In this dialogue system, user utterances (text input) are transmitted to a **response generation server** hosted on **Heroku**. The system leverages **Actions on Google** and **Dialogue Flow** to forward user utterances to the server. The server then generates responses based on the input, which are used to create an interactive dialogue experience for the user.

---

## 🏷️ **Optional Badges**

Add the following badges to your `README.md` to give it a more professional and visually appealing look:

- 📝 **Webhook**: ![Webhook](https://img.shields.io/badge/Webhook-Enabled-green)
- 🚀 **Heroku Deployment**: ![Heroku](https://img.shields.io/badge/Heroku-Deployed-blueviolet)
- 🗣️ **Dialogue Flow Integration**: ![Dialogue Flow](https://img.shields.io/badge/DialogueFlow-v2-blue)
- 📡 **POST Request**: ![POST Request](https://img.shields.io/badge/Request-POST-blue)
- 🌐 **HTTP Protocol**: ![HTTP](https://img.shields.io/badge/Protocol-HTTP-yellow)
- 🎤 **Actions on Google**: ![Actions on Google](https://img.shields.io/badge/Actions_on_Google-Integrated-red)
- 💬 **Response Generation Server**: ![Response Server](https://img.shields.io/badge/Response-Generated-orange)


## 🎯 旅行予約タスクを持った対話システム評価 実験 (日本語用)

## 実験の目的と概要

本研究では、課題4および課題5で作成した対話システムの評価を行います。1回の対話施行では、システムの応答の多様性を正確に評価することが難しいため、各評価者には2回の対話施行を実施してもらいます。
その後、実装した接客エージェントに対し、どの程度のホスピタリティを感じたかに則った「評価シート」による評価を行います。本研究の目的は、ホスピタリティが与える対話システムに対する満足度の影響度を調査することです。

### 実験のやり方

実験に際しては、まず実験のやり方を説明した上で、実験を行ってもらいます。もし、実験の内容に質問があれば、ご自由におたずねください。
納得いくまでご説明いたします。実験中には何度か短い休憩を挟みます。実験が終了した後でも、疑問に感じたことなどがありましたら、遠慮なくおたずねください。

### 実験に要する時間

- 実験は、1回当たり5分程度で終了する予定です。

### 個人情報の取り扱い

実験によって得られたデータについては、統計的に処理した結果のみを学会等で発表し、個別的なデータを個人が特定可能な形で公開することはありません。
また、個人情報を含むすべてのデータは、外部に漏洩することのないように匿名化して厳重に管理し、個人情報については再実験または事故が生じたときの連絡以外の目的には使用いたしません。

### 謝金

- 無償でのご協力、ありがとうございます。

### 実験の安全性

計測には、安全性の十分に確かめられた専用の装置を用いますので、身体への影響や危険は一切伴いません。

### 不安を感じた場合の配慮

もし実験手続きに不安を感じたり、疑問が湧いたりした場合には、遠慮せずに申し出てください。
できるだけ、説明しご理解いただけるように努力します。また、実験結果に関しても、不安を感じる場合は、納得いただけるまでご説明いたします。

### 実験中止の申し出

疑問や不安が解消せず、実験の継続ができないと感じた場合や、実験の手続きにおいて著しい不快感を覚えた場合には、遠慮なく申し出てください。
その場合、即座に実験は中断または中止いたします。そのことで、あなたが不利な扱いを受けることはいかなる点においてもありません。

---

## 評価アンケート

### 評価項目

具体的な評価質問項目は以下の通りです。各評価項目に対して、1〜5点の5段階評価を行います。

1. **流暢性**  
   システムの応答が自然でスムーズであったかどうかを評価します。

2. **共感性**  
   システムがユーザの感情や状況にどれだけ共感的に応じたかを評価します。

3. **興味性**  
   対話中にユーザがどれだけ興味を持ったかを評価します。

4. **もう一度話したいか**  
   対話後にユーザが再度システムとの対話を希望するかどうかを評価します。

---

### 感謝の言葉

ご協力いただき、誠にありがとうございます。本研究は、対話システムの改善に向けた重要な一歩となります。あなたの貴重な意見が、今後の研究に大いに役立つことを期待しています。引き続きよろしくお願いいたします。
