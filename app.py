from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Sarakham RideShare MVP", page_icon="🚗", layout="wide"
)

st.title("🚗 ระบบจับคู่และคำนวณหารค่าเดินทางร่วมกัน (มมส / มหาสารคาม)")
st.caption(
    "โครงการออกแบบ MVP จากปัญหาจริง | นิสิต สาขาวิทยาการข้อมูลประยุกต์"
)

# Sidebar toggle for MVP Version Comparison
st.sidebar.header("⚙️ การเลือกเวอร์ชัน MVP")
mvp_version = st.sidebar.radio(
    "เลือกรุ่นที่ต้องการทดสอบ:",
    ["MVP 1 (Core Version)", "MVP 2 (Iterated Version from Feedback)"],
)

st.sidebar.markdown("---")
st.sidebar.info("""
**สรุปการพัฒนา (Iteration):**
- **MVP 1:** จับคู่เส้นทางพื้นฐาน + คำนวณหารเท่ากัน
- **MVP 2:** เพิ่มตัวกรองเพศ + กรองรถว่าง + คำนวณตามระยะทาง (ลงกลางทาง) + ปุ่มขอร่วมทริปพร้อมเลขพร้อมเพย์
""")

# Sample Data (Synthetic Data for Prototype)
if "trips" not in st.session_state:
  st.session_state.trips = [
      {
          "id": 1,
          "creator": "นิสิต ก. (คณะวิทยาการสารสนเทศ)",
          "gender": "หญิง",
          "type": "เทศกาล/ต่างจังหวัด",
          "origin": "หอพักแถวขามเรียง (ม.ใหม่)",
          "destination": "สนามบินขอนแก่น",
          "date": "2026-10-12",
          "time": "08:30",
          "total_fare": 800,
          "max_seats": 4,
          "current_seats": 2,
          "contact": "Line ID: nisit_k12",
          "promptpay": "081-234-XXXX",
          "note": "มีกระเป๋าเดินทางใบใหญ่ 1 ใบค่ะ",
      },
      {
          "id": 2,
          "creator": "นิสิต ข. (คณะมนุษยศาสตร์)",
          "gender": "ชาย",
          "type": "รายวัน/ไป-กลับ มหาลัย",
          "origin": "อาคารพลาญชัย (ม.เก่า)",
          "destination": "ตลาดน้อย (ม.ใหม่)",
          "date": "2026-10-10",
          "time": "16:40",
          "total_fare": 120,
          "max_seats": 3,
          "current_seats": 3,
          "contact": "Line ID: nisit_b34",
          "promptpay": "089-876-XXXX",
          "note": "หารค่าแท็กซี่กลับมหาลัยครับ",
      },
  ]

tab1, tab2, tab3 = st.tabs([
    "🔍 ค้นหา & จับคู่รถ",
    "➕ โพสต์หารค่ารถ",
    "🧮 เครื่องมือคำนวณค่าเดินทาง (Split Fare Calculator)",
])

# ----------------- TAB 1: SEARCH & MATCHING -----------------
with tab1:
  st.subheader("🔍 ค้นหาเที่ยวเดินทางที่ตรงกัน")
  col1, col2, col3 = st.columns(3)
  with col1:
    search_origin = st.selectbox(
        "ต้นทาง",
        [
            "ทั้งหมด",
            "หอพักแถวขามเรียง (ม.ใหม่)",
            "อาคารพลาญชัย (ม.เก่า)",
            "บขส.มหาสารคาม",
        ],
    )
  with col2:
    search_dest = st.selectbox(
        "ปลายทาง",
        [
            "ทั้งหมด",
            "สนามบินขอนแก่น",
            "สถานีรถไฟขอนแก่น",
            "ตลาดน้อย (ม.ใหม่)",
            "บขส.มหาสารคาม",
        ],
    )
  with col3:
    search_type = st.selectbox(
        "ประเภทการเดินทาง",
        ["ทั้งหมด", "รายวัน/ไป-กลับ มหาลัย", "เทศกาล/ต่างจังหวัด"],
    )

  # MVP 2 Feature: Extra Filters based on Feedback
  if mvp_version == "MVP 2 (Iterated Version from Feedback)":
    st.markdown(
        "**🛡️ ตัวกรองเพิ่มเติม (MVP 2 - เพิ่มตาม Feedback เรื่องความปลอดภัย):**"
    )
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      filter_gender = st.selectbox(
          "จำกัดเพศผู้ร่วมเดินทาง",
          ["แสดงทั้งหมด", "เฉพาะผู้หญิง", "เฉพาะผู้ชาย"],
      )
    with col_f2:
      hide_full = st.checkbox("ซ่อนคันที่นั่งเต็มแล้ว", value=True)

  st.markdown("---")

  filtered_trips = st.session_state.trips
  if search_origin != "ทั้งหมด":
    filtered_trips = [t for t in filtered_trips if t["origin"] == search_origin]
  if search_dest != "ทั้งหมด":
    filtered_trips = [
        t for t in filtered_trips if t["destination"] == search_dest
    ]
  if search_type != "ทั้งหมด":
    filtered_trips = [t for t in filtered_trips if t["type"] == search_type]

  if mvp_version == "MVP 2 (Iterated Version from Feedback)":
    if filter_gender == "เฉพาะผู้หญิง":
      filtered_trips = [t for t in filtered_trips if t["gender"] == "หญิง"]
    elif filter_gender == "เฉพาะผู้ชาย":
      filtered_trips = [t for t in filtered_trips if t["gender"] == "ชาย"]

    if hide_full:
      filtered_trips = [
          t for t in filtered_trips if t["current_seats"] < t["max_seats"]
      ]

  st.write(f"พบการเดินทางที่ตรงกัน: **{len(filtered_trips)}** รายการ")

  for trip in filtered_trips:
    fare_per_person = trip["total_fare"] / max(1, trip["current_seats"])
    is_full = trip["current_seats"] >= trip["max_seats"]

    with st.container(border=True):
      col_a, col_b = st.columns([5, 2])
      with col_a:
        status_badge = "🔴 เต็มแล้ว" if is_full else "🟢 ยังรับได้อีก"
        st.markdown(
            f"#### 🚗 {trip['origin']} ➔ {trip['destination']} `{status_badge}`"
        )
        st.write(
            f"📅 **วัน-เวลา:** {trip['date']} @ {trip['time']} น. | 📌"
            f" **ประเภท:** {trip['type']}"
        )
        st.write(
            f"👤 **ผู้โพสต์:** {trip['creator']} ({trip['gender']}) | 💬"
            f" **หมายเหตุ:** {trip['note']}"
        )
      with col_b:
        st.metric(label="ค่ารถประมาณ/คน", value=f"฿{fare_per_person:.0f}")
        st.write(
            f"👥 ที่นั่งว่าง:"
            f" **{trip['max_seats'] - trip['current_seats']}**/{trip['max_seats']}"
            " ที่"
        )

        if mvp_version == "MVP 1 (Core Version)":
          if st.button("ดูช่องทางติดต่อ", key=f"btn_mvp1_{trip['id']}"):
            st.info(f"ติดต่อ: {trip['contact']}")
        else:
          if is_full:
            st.error("ที่นั่งเต็มแล้ว")
          else:
            with st.popover("📲 ขอร่วมหาร & โอนเงิน"):
              st.write(f"**ช่องทางติดต่อ:** {trip['contact']}")
              st.write(f"**พร้อมเพย์:** {trip['promptpay']}")
              st.caption("แนะนำให้ทักแชตตกลงเวลาก่อนโอนมัดจำ")

# ----------------- TAB 2: POST RIDE -----------------
with tab2:
  st.subheader("➕ ลงประกาศหาเพื่อนหารค่ารถ")
  with st.form("post_ride_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
      post_creator = st.text_input("ชื่อ/นามแฝง", "นิสิต มมส.")
      post_gender = st.selectbox("เพศของคุณ", ["หญิง", "ชาย", "ไม่ระบุ"])
      post_type = st.selectbox(
          "ประเภทการเดินทาง",
          ["เทศกาล/ต่างจังหวัด", "รายวัน/ไป-กลับ มหาลัย"],
      )
      post_origin = st.text_input("จุดเริ่มต้น", "หอพักแถวขามเรียง (ม.ใหม่)")
      post_dest = st.text_input("ปลายทาง", "สนามบินขอนแก่น")
    with c2:
      post_date = st.date_input("วันที่เดินทาง", value=date.today())
      post_time = st.time_input("เวลาโดยประมาณ", value=datetime.now().time())
      post_fare = st.number_input(
          "ค่ารถรวมทั้งหมด (บาท)", min_value=50, value=800, step=50
      )
      post_seats = st.number_input(
          "จำนวนรับได้สูงสุด (รวมตัวเอง)", min_value=2, value=4, step=1
      )
      post_contact = st.text_input(
          "ช่องทางติดต่อ (Line ID / เบอร์)", "Line: nisit_demo"
      )
      post_promptpay = st.text_input(
          "เบอร์พร้อมเพย์ (สำหรับหารค่ารถ)", "08X-XXX-XXXX"
      )

    post_note = st.text_area("หมายเหตุเพิ่มเติม", "มีกระเป๋าเดินทาง 1 ใบ")
    submit = st.form_submit_button("🚀 ลงประกาศเดินทาง")

    if submit:
      new_trip = {
          "id": len(st.session_state.trips) + 1,
          "creator": post_creator,
          "gender": post_gender,
          "type": post_type,
          "origin": post_origin,
          "destination": post_dest,
          "date": str(post_date),
          "time": post_time.strftime("%H:%M"),
          "total_fare": post_fare,
          "max_seats": post_seats,
          "current_seats": 1,
          "contact": post_contact,
          "promptpay": (
              post_promptpay
              if mvp_version == "MVP 2 (Iterated Version from Feedback)"
              else "ไม่ได้เปิดเผยใน MVP 1"
          ),
          "note": post_note,
      }
      st.session_state.trips.append(new_trip)
      st.success("ลงประกาศเรียบร้อยแล้ว! สามารถดูได้ที่แท็บค้นหา")

# ----------------- TAB 3: SPLIT FARE CALCULATOR -----------------
with tab3:
  st.subheader("🧮 เครื่องมือคำนวณหารค่ารถ (Split Fare Calculator)")
  if mvp_version == "MVP 1 (Core Version)":
    st.info("📌 **MVP 1 Mode:** คำนวณแบบหารเท่ากันทุกคน (Equal Split)")
    total_cost = st.number_input("ค่ารถรวมทั้งหมด (บาท)", value=800, key="c1")
    num_people = st.number_input(
        "จำนวนคนทั้งหมด", value=4, min_value=1, key="n1"
    )
    st.metric("ยอดที่ต้องจ่ายคนละ", f"฿{(total_cost/num_people):.2f} บาท")
  else:
    st.success("📌 **MVP 2 Mode (ตาม Feedback):** เลือกรูปแบบการหารได้")
    calc_mode = st.radio(
        "เลือกรูปแบบการหาร:",
        ["หารเท่ากันทุกคน", "หารตามสัดส่วนระยะทาง (ลงกลางทาง)"],
    )

    if calc_mode == "หารเท่ากันทุกคน":
      total_cost = st.number_input("ค่ารถรวมทั้งหมด (บาท)", value=800, key="c2")
      num_people = st.number_input(
          "จำนวนคนทั้งหมด", value=4, min_value=1, key="n2"
      )
      st.metric("ยอดที่ต้องจ่ายคนละ", f"฿{(total_cost/num_people):.2f} บาท")
    else:
      st.write("##### 📏 คำนวณแบบแวะลงกลางทาง (Weighted Fare)")
      total_cost = st.number_input(
          "ค่ารถรวมตามมิเตอร์/เหมา (บาท)", value=600, key="c3"
      )
      p1_dist = st.number_input(
          "ระยะทางคนแรก (ลง บขส.สารคาม) - กม.", value=10.0
      )
      p2_dist = st.number_input(
          "ระยะทางคนที่สอง (ลง สนามบินขอนแก่น) - กม.", value=50.0
      )
      total_dist = p1_dist + p2_dist
      if total_dist > 0:
        p1_pay = total_cost * (p1_dist / total_dist)
        p2_pay = total_cost * (p2_dist / total_dist)
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("คนลงจุด A จ่าย", f"฿{p1_pay:.2f} บาท")
        col_r2.metric("คนลงปลายทาง B จ่าย", f"฿{p2_pay:.2f} บาท")
