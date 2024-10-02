<div align="center">

[![Tour Reservations](https://img.shields.io/badge/Tours-Reservation-orange)](https://yourlink.com)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
[![Flask](https://img.shields.io/badge/Flask-v2.0.2-blue)](https://palletsprojects.com/p/flask/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-brightgreen)](https://www.python.org/)

[![Dialogue Flow](https://img.shields.io/badge/DialogueFlow-v2-blue)](https://dialogflow.cloud.google.com/)
[![Heroku](https://img.shields.io/badge/Heroku-Deployed-blueviolet)](https://www.heroku.com/)
[![Git](https://img.shields.io/badge/Git-Repository-orange)](https://git-scm.com/)

# Tour Reservation System (`app4.py`)

**A Flask-based web application for booking and managing tour reservations.**

This system allows users to choose from three exciting tour options: **温泉ツアー (Onsen Tour)**, **遊園地ツアー (Amusement Park Tour)**, and **バスツアー (Bus Tour)**. Each tour has specific rules for availability and pricing.

</div>

## 🚶‍♂️ **Tour Options & Reservation Rules**

### 1. **温泉ツアー (Onsen Tour)**

- **Available Locations**:
  - 登別 (Noboribetsu)
  - 有馬 (Arima)
  - 別府 (Beppu)
  - 草津 (Kusatsu)
  - 白浜 (Shirahama)

- **Reservation Rules**:
  - **April**: Reservations are **unavailable** for all locations.
  - **Saturdays**: Afternoon (PM) slots are typically fully booked.

---

### 2. **遊園地ツアー (Amusement Park Tour)**

- **Available Locations**:
  - USJ (Universal Studios Japan)
  - ディズニーランド (Disneyland)
  - ディズニーシー (DisneySea)
  - 花やしき (Hanayashiki)
  - ひらかたパーク (Hirakata Park)

- **Reservation Rules**:
  - **March 15 - March 31**: Reservations are **unavailable** for all locations.
  - **Weekends**: Higher likelihood of full bookings.
  - **Crowded Locations**: USJ, ディズニーランド, and ディズニーシー have a **higher booking rate**.

---

### 3. **バスツアー (Bus Tour)**

- **Available Locations**:
  - 中華街 (Chinatown)
  - 黒潮市場 (Kuroshio Market)
  - 姫路城 (Himeji Castle)

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

---

## 📅 **Schedule Format:**

The system uses a schedule format (`schedule.txt`) to display booking availability and reserved slots.

Example for **温泉ツアー (Onsen Tour)** at **登別**:

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

## 🔧 **Installation**

1. Clone the repository:

    ```bash
    git clone https://github.com/banban1029/junior_ws.git
    cd ~/junior_ws/interactive_system
    ```

2. Install dependencies:

    comming soon

3. Run the application:

    ```bash
    python app4.py
    ```

4. Access the system at `http://localhost:5000( comming soon )` in your web browser.

## 📝 **Contributing**

Comming soon

---

## 📜 **License**

Nothing

---
Here’s an improved version of the `README.md` section with enhanced formatting:

---

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

---

This version maintains clarity while adding a touch of visual appeal through the optional badges. You can adjust the badge links and colors to match your preferences!