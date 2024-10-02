# Tour Reservation System (app4.py)

This is a Flask-based web application that simulates tour reservations. Users can choose from three different types of tours: 温泉ツアー (Onsen Tour), 遊園地ツアー (Amusement Park Tour), and バスツアー (Bus Tour). Each tour has specific rules regarding reservation availability and pricing.

## Activity Information

### 1. **温泉ツアー (Onsen Tour)**
- **Available Locations**:
  - 登別 (Noboribetsu)
  - 有馬 (Arima)
  - 別府 (Beppu)
  - 草津 (Kusatsu)
  - 白浜 (Shirahama)

- **Reservation Rules**:
  - **April**: Reservations are **unavailable** for all locations.
  - **Saturdays**: Typically, **afternoon slots** (PM) are more likely to be fully booked.

### 2. **遊園地ツアー (Amusement Park Tour)**
- **Available Locations**:
  - USJ (Universal Studios Japan)
  - ディズニーランド (Disneyland)
  - ディズニーシー (DisneySea)
  - 花やしき (Hanayashiki)
  - ひらかたパーク (Hirakata Park)
  
- **Reservation Rules**:
  - **March 15 - March 31**: Reservations are **unavailable** for all locations.
  - **Weekends**: More likely to be fully booked compared to weekdays.
  - **Crowded Locations**: USJ, ディズニーランド, and ディズニーシー have a **higher booking rate** .

### 3. **バスツアー (Bus Tour)**
- **Available Locations**:
  - 中華街 (Chinatown)
  - 黒潮市場 (Kuroshio Market)
  - 姫路城 (Himeji Castle)
  
- **Reservation Rules**:
  - **Weekday mornings**: No reservations available.
  - **Weekdays and weekends**: Have similar booking **lower booking rate** .

## Additional Features

- **Dynamic Booking**: The system randomly generates booked slots to simulate real-world availability.
- **Booking Rates**: Different activities and locations have varying booking rates based on popularity and day of the week.
- **Validation**: Ensures users can only book valid locations and dates.
- **Pricing**: Dynamic pricing is implemented for each location based on predefined budget data.


## Using `schedule.txt` 

```
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


