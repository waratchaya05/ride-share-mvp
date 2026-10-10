from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="UniRide Share (มมส. & ทั่วไทย)",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 ระบบจับคู่และคำนวณหารค่าเดินทางร่วมกัน (UniRide)")
st.caption("เชื่อมต่อการเดินทางทั้งภายในพื้นที่ มมส. / สารคาม และเดินทางข้ามจังหวัดทั่วประเทศ")

# ข้อมูลสถานที่สำคัญรอบ มมส. / มหาสารคาม
CAMPUS_LOCATIONS = [
    "มมส. ม.ใหม่ (ขามเรียง) - หน้าป้ายมอ",
    "มมส. ม.ใหม่ (ขามเรียง) - ตลาดน้อย / อาคารกองกิจ",
    "มมส. ม.ใหม่ (ขามเรียง) - คณะวิทยาการสารสนเทศ / SC",
    "มมส. ม.เก่า (ในเมือง) - คณะแพทย์ศาสตร์",
    "หอพักโซนขามเรียง",
    "หอพักโซนท่าขอนยาง",
    "บขส. มหาสารคาม",
    "เสริมไทยคอมเพล็กซ์ มหาสารคาม",
    "สถานีรถไฟบรบือ / เมืองมหาสารคาม"
]

# รายชื่อ 77 จังหวัดทั่วไทย
PROVINCES = [
    "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร", "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา",
    "ชลบุรี", "ชัยนาท", "ชัยภูมิ", "ชุมพร", "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "ตาก", "นครนายก",
    "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์", "นนทบุรี", "นราธิวาส", "น่าน",
    "บึงกาฬ", "บุรีรัมย์", "ปทุมธานี", "ประจวบคีรีขันธ์", "ปราจีนบุรี", "ปัตตานี", "พระนครศรีอยุธยา",
    "พังงา", "พัทลุง", "พิจิตร", "พิษณุโลก", "เพชรบุรี", "เพชรบูรณ์", "แพร่", "พะเยา", "ภูเก็ต",
    "มหาสารคาม", "มุกดาหาร", "แม่ฮ่องสอน", "ยะลา", "ยโสธร", "ร้อยเอ็ด", "ระนอง", "ระยอง", "ราชบุรี",
    "ลพบุรี", "ลำปาง", "ลำพูน", "เลย", "ศรีสะเกษ", "สกลนคร", "สงขลา", "สตูล", "สมุทรปราการ",
    "สมุทรสงคราม", "สมุทรสาคร", "สระแก้ว", "สระบุรี", "สิงห์บุรี", "สุโขทัย", "สุพรรณบุรี", "สุราษฎร์ธานี",
    "สุรินทร์", "หนองคาย", "หนองบัวลำภู", "อ่างทอง", "อำนาจเจริญ", "อุดรธานี", "อุตรดิตถ์", "อุทัยธานี", "อุบลราชธานี"
]

# Sidebar toggle for MVP Version Comparison
st.sidebar.header("⚙️ การเลือกเวอร์ชัน MVP")
mvp_version = st.sidebar.radio(
    "เลือกรุ่นที่ต้องการทดสอบ:",
    ["MVP 1 (Core Version)", "MVP 2 (Iterated Version from Feedback)"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**สรุปการพัฒนา (Iteration):**
- **MVP 1:** ค้นหาจับคู่ตามขอบเขต (มมส. หรือ ทั่วไทย) + หารเท่ากัน
- **MVP 2:** เพิ่มตัวกรองเพศ + ซ่อนคันที่เต็ม + รองรับหารตามระยะทางแวะลงกลางทาง + ปุ่มคัดลอกช่องทางชำระเงิน/พร้อมเพย์
""")

# ข้อมูลจำลอง (Synthetic Data) ครอบคลุมทั้งสองระดับ
if "trips" not in st.session_state:
    st.session_state.trips = [
        {
            "id": 1,
            "scope": "ภายใน มมส. / สารคาม",
            "creator": "นิสิต ก. (IT มมส.)",
            "gender": "หญิง",
            "type": "รายวัน/ไป-กลับ เรียน",
            "origin": "หอพักโซนท่าขอนยาง",
            "destination": "มมส. ม.ใหม่ (ขามเรียง) - คณะวิทยาการสารสนเทศ / SC",
            "date": "2026-10-12",
            "time": "08:15",
            "total_fare": 60,
            "max_seats": 3,
            "current_seats": 1,
            "contact": "Line ID: nisit_it01",
            "promptpay": "081-111-XXXX",
            "note": "หารค่าวิน/แท็กซี่ไปเรียนเช้าค่ะ"
        },
        {
            "id": 2,
            "scope": "ภายใน มมส. / สารคาม",
            "creator": "นิสิต ข. (มนุษยศาสตร์)",
            "gender": "ชาย",
            "type": "เดินทางข้ามมอ (ม.เก่า - ม.ใหม่)",
            "origin": "มมส. ม.เก่า (ในเมือง) - อาคารพลาญชัย",
            "destination": "มมส. ม.ใหม่ (ขามเรียง) - ตลาดน้อย / อาคารกองกิจ",
            "date": "2026-10-12",
            "time": "16:40",
            "total_fare": 120,
            "max_seats": 4,
            "current_seats": 2,
            "contact": "Line ID: nisit_human",
            "promptpay": "082-222-XXXX",
            "note": "มีธุระเข้า ม.ใหม่ ใครกลับพร้อมกันทักได้ครับ"
        },
        {
            "id": 3,
            "scope": "ข้ามจังหวัดทั่วประเทศ",
            "creator": "นิสิต ค. (เภสัชศาสตร์)",
            "gender": "หญิง",
            "type": "กลับภูมิลำเนา/เทศกาล",
            "origin": "มหาสารคาม (หน้า ม.ใหม่ ขามเรียง)",
            "destination": "ขอนแก่น (สนามบินขอนแก่น)",
            "date": "2026-10-15",
            "time": "09:00",
            "total_fare": 800,
            "max_seats": 4,
            "current_seats": 2,
            "contact": "Line ID: rx_trip",
            "promptpay": "083-333-XXXX",
            "note": "เหมารถแท็กซี่ไปขึ้นเครื่อง มีกระเป๋าใบใหญ่ 1 ใบ"
        },
        {
            "id": 4,
            "scope": "ข้ามจังหวัดทั่วประเทศ",
            "creator": "นาย ง. (บุคลากร)",
            "gender": "ชาย",
            "type": "เดินทางไปทำงาน/ประชุม",
            "origin": "มหาสารคาม (บขส.สารคาม)",
            "destination": "กรุงเทพมหานคร (หมอชิต 2 / รังสิต)",
            "date": "2026-10-16",
            "time": "06:30",
            "total_fare": 2200,
            "max_seats": 4,
            "current_seats": 3,
            "contact": "Line ID: officer_travel",
            "promptpay": "084-444-XXXX",
            "note": "รถยนต์ส่วนตัว หารค่าน้ำมัน ไม่สูบบุหรี่"
        }
    ]

tab1, tab2, tab3 = st.tabs([
    "🔍 ค้นหาเที่ยวเดินทาง",
    "➕ ลงประกาศหาเพื่อนหารค่ารถ",
    "🧮 เครื่องมือคำนวณค่าเดินทาง (Split Fare Calculator)"
])

# ----------------- TAB 1: SEARCH & MATCHING -----------------
with tab1:
    st.subheader("🔍 ค้นหาเที่ยวเดินทางที่ตรงกัน")
    
    col_scope, col_type = st.columns([1, 1])
    with col_scope:
        filter_scope = st.radio("เลือกขอบเขตพื้นที่การเดินทาง:", ["ทั้งหมด", "ภายใน มมส. / สารคาม", "ข้ามจังหวัดทั่วประเทศ"], horizontal=True)
    with col_type:
        filter_type = st.selectbox("ประเภทการเดินทาง", ["ทั้งหมด", "รายวัน/ไป-กลับ เรียน", "เดินทางข้ามมอ (ม.เก่า - ม.ใหม่)", "กลับภูมิลำเนา/เทศกาล", "เดินทางไปทำงาน/ประชุม"])

    col1, col2 = st.columns(2)
    if filter_scope == "ภายใน มมส. / สารคาม":
        with col1:
            search_origin = st.selectbox("จุดเริ่มต้น (ใน มมส. / สารคาม)", ["ทั้งหมด"] + CAMPUS_LOCATIONS)
        with col2:
            search_dest = st.selectbox("จุดหมายปลายทาง (ใน มมส. / สารคาม)", ["ทั้งหมด"] + CAMPUS_LOCATIONS)
    elif filter_scope == "ข้ามจังหวัดทั่วประเทศ":
        with col1:
            search_origin = st.selectbox("จังหวัดต้นทาง", ["ทั้งหมด"] + PROVINCES)
        with col2:
            search_dest = st.selectbox("จังหวัดปลายทาง", ["ทั้งหมด"] + PROVINCES)
    else:
        with col1:
            search_origin = st.text_input("ค้นหาจุดต้นทาง (พิมพ์ชื่อจุดหรือจังหวัด)", "")
        with col2:
            search_dest = st.text_input("ค้นหาปลายทาง (พิมพ์ชื่อจุดหรือจังหวัด)", "")

    # MVP 2 Additional Filters
    if mvp_version == "MVP 2 (Iterated Version from Feedback)":
        st.markdown("**🛡️ ตัวกรองเพิ่มเติม (MVP 2 - ความปลอดภัย & ความสะดวก):**")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_gender = st.selectbox("จำกัดเพศผู้ร่วมเดินทาง", ["แสดงทั้งหมด", "เฉพาะผู้หญิง", "เฉพาะผู้ชาย"])
        with col_f2:
            hide_full = st.checkbox("ซ่อนคันที่นั่งเต็มแล้ว", value=True)

    st.markdown("---")

    # Filtering Logic
    filtered_trips = st.session_state.trips
    if filter_scope != "ทั้งหมด":
        filtered_trips = [t for t in filtered_trips if t["scope"] == filter_scope]
    if filter_type != "ทั้งหมด":
        filtered_trips = [t for t in filtered_trips if t["type"] == filter_type]

    if search_origin and search_origin != "ทั้งหมด":
        filtered_trips = [t for t in filtered_trips if search_origin in t["origin"]]
    if search_dest and search_dest != "ทั้งหมด":
        filtered_trips = [t for t in filtered_trips if search_dest in t["destination"]]

    if mvp_version == "MVP 2 (Iterated Version from Feedback)":
        if filter_gender == "เฉพาะผู้หญิง":
            filtered_trips = [t for t in filtered_trips if t["gender"] == "หญิง"]
        elif filter_gender == "เฉพาะผู้ชาย":
            filtered_trips = [t for t in filtered_trips if t["gender"] == "ชาย"]

        if hide_full:
            filtered_trips = [t for t in filtered_trips if t["current_seats"] < t["max_seats"]]

    st.write(f"พบการเดินทางที่ตรงกัน: **{len(filtered_trips)}** รายการ")

    for trip in filtered_trips:
        fare_per_person = trip["total_fare"] / max(1, trip["current_seats"])
        is_full = trip["current_seats"] >= trip["max_seats"]

        with st.container(border=True):
            col_a, col_b = st.columns([5, 2])
            with col_a:
                badge_color = "red" if is_full else "green"
                status_badge = "🔴 เต็มแล้ว" if is_full else "🟢 ยังรับได้อีก"
                scope_tag = f"🏫 {trip['scope']}" if "มมส." in trip["scope"] else f"🇹🇭 {trip['scope']}"
                st.markdown(f"#### 🚗 {trip['origin']} ➔ {trip['destination']}")
                st.caption(f"**ขอบเขต:** `{scope_tag}` | **สถานะ:** `{status_badge}` | **ประเภท:** {trip['type']}")
                st.write(f"📅 **วัน-เวลา:** {trip['date']} @ {trip['time']} น.")
                st.write(f"👤 **ผู้โพสต์:** {trip['creator']} ({trip['gender']}) | 💬 **หมายเหตุ:** {trip['note']}")
            with col_b:
                st.metric(label="ค่ารถประมาณ/คน", value=f"฿{fare_per_person:.0f}")
                st.write(f"👥 ที่นั่งว่าง: **{trip['max_seats'] - trip['current_seats']}**/{trip['max_seats']} ที่")

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
                            st.caption("แนะนำให้ทักแชตตกลงเวลาและจุดรับก่อนโอนเงิน")

# ----------------- TAB 2: POST RIDE -----------------
with tab2:
    st.subheader("➕ ลงประกาศหาเพื่อนหารค่ารถ")
    with st.form("post_ride_form", clear_on_submit=True):
        c_scope = st.radio("เลือกขอบเขตการเดินทางของทริปนี้:", ["ภายใน มมส. / สารคาม", "ข้ามจังหวัดทั่วประเทศ"], horizontal=True)
        
        c1, c2 = st.columns(2)
        with c1:
            post_creator = st.text_input("ชื่อ/นามแฝง", "นิสิต มมส.")
            post_gender = st.selectbox("เพศของคุณ", ["หญิง", "ชาย", "ไม่ระบุ"])
            
            if c_scope == "ภายใน มมส. / สารคาม":
                post_type = st.selectbox("ประเภทการเดินทาง", ["รายวัน/ไป-กลับ เรียน", "เดินทางข้ามมอ (ม.เก่า - ม.ใหม่)", "ไปตลาด/ห้างสรรพสินค้า"])
                post_origin = st.selectbox("จุดเริ่มต้น", CAMPUS_LOCATIONS)
                post_dest = st.selectbox("จุดหมายปลายทาง", CAMPUS_LOCATIONS, index=1)
            else:
                post_type = st.selectbox("ประเภทการเดินทาง", ["กลับภูมิลำเนา/เทศกาล", "ท่องเที่ยว/ทริปวันหยุด", "เดินทางไปทำงาน/ประชุม"])
                p_orig_prov = st.selectbox("จังหวัดต้นทาง", PROVINCES, index=PROVINCES.index("มหาสารคาม"))
                p_orig_detail = st.text_input("จุดนัดพบย่อย (ต้นทาง)", "หน้า ม.ใหม่ ขามเรียง")
                p_dest_prov = st.selectbox("จังหวัดปลายทาง", PROVINCES, index=PROVINCES.index("ขอนแก่น"))
                p_dest_detail = st.text_input("จุดส่งย่อย (ปลายทาง)", "สนามบินขอนแก่น")
                post_origin = f"{p_orig_prov} ({p_orig_detail})"
                post_dest = f"{p_dest_prov} ({p_dest_detail})"

        with c2:
            post_date = st.date_input("วันที่เดินทาง", value=date.today())
            post_time = st.time_input("เวลาโดยประมาณ", value=datetime.now().time())
            default_fare = 80 if c_scope == "ภายใน มมส. / สารคาม" else 1500
            post_fare = st.number_input("ค่ารถรวมทั้งหมด / ค่าน้ำมัน (บาท)", min_value=20, value=default_fare, step=20)
            post_seats = st.number_input("จำนวนรับได้สูงสุด (รวมตัวเอง)", min_value=2, value=4, step=1)
            post_contact = st.text_input("ช่องทางติดต่อ (Line ID / เบอร์โทร)", "Line: nisit_demo")
            post_promptpay = st.text_input("เบอร์พร้อมเพย์ (สำหรับหารค่ารถ)", "08X-XXX-XXXX")

        post_note = st.text_area("หมายเหตุเพิ่มเติม", "สัมภาระ / สไตล์การเดินทาง / เงื่อนไขอื่น ๆ")
        submit = st.form_submit_button("🚀 ลงประกาศเดินทาง")

        if submit:
            new_trip = {
                "id": len(st.session_state.trips) + 1,
                "scope": c_scope,
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
                "promptpay": post_promptpay if mvp_version == "MVP 2 (Iterated Version from Feedback)" else "ไม่ได้เปิดเผยใน MVP 1",
                "note": post_note
            }
            st.session_state.trips.append(new_trip)
            st.success("ลงประกาศเรียบร้อยแล้ว! ข้อมูลจะปรากฏในแท็บค้นหาทันที")

# ----------------- TAB 3: SPLIT FARE CALCULATOR -----------------
with tab3:
    st.subheader("🧮 เครื่องมือคำนวณหารค่ารถ (Split Fare Calculator)")
    if mvp_version == "MVP 1 (Core Version)":
        st.info("📌 **MVP 1 Mode:** คำนวณแบบหารเท่ากันทุกคน (Equal Split)")
        total_cost = st.number_input("ค่าใช้จ่ายรวมทั้งหมด (บาท)", value=120, key="c1")
        num_people = st.number_input("จำนวนคนทั้งหมด", value=3, min_value=1, key="n1")
        st.metric("ยอดที่ต้องจ่ายคนละ", f"฿{(total_cost/num_people):.2f} บาท")
    else:
        st.success("📌 **MVP 2 Mode (ตาม Feedback):** รองรับทั้งแบบหารเท่า และแวะลงระหว่างทาง")
        calc_mode = st.radio("เลือกรูปแบบการหาร:", ["หารเท่ากันทุกคน", "หารตามสัดส่วนระยะทาง (เช่น นั่งลงกลางทาง)"])

        if calc_mode == "หารเท่ากันทุกคน":
            total_cost = st.number_input("ค่าใช้จ่ายรวมทั้งหมด (บาท)", value=120, key="c2")
            num_people = st.number_input("จำนวนคนทั้งหมด", value=3, min_value=1, key="n2")
            st.metric("ยอดที่ต้องจ่ายคนละ", f"฿{(total_cost/num_people):.2f} บาท")
        else:
            st.write("##### 📏 ตัวอย่าง: นั่งรถจาก ม.ใหม่ ขามเรียง ➔ บขส. สารคาม (คนแรกลง เสริมไทยฯ)")
            total_cost = st.number_input("ค่ารถรวมตามเหมา/มิเตอร์ (บาท)", value=150, key="c3")
            p1_dist = st.number_input("ระยะทางคนแรกลงกลางทาง (กม.)", value=4.0)
            p2_dist = st.number_input("ระยะทางคนที่สองลงปลายทาง (กม.)", value=10.0)
            total_dist = p1_dist + p2_dist
            if total_dist > 0:
                p1_pay = total_cost * (p1_dist / total_dist)
                p2_pay = total_cost * (p2_dist / total_dist)
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("คนลงจุดแรก จ่าย", f"฿{p1_pay:.2f} บาท")
                col_r2.metric("คนลงปลายทาง จ่าย", f"฿{p2_pay:.2f} บาท")
