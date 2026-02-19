# Lab_66010789
ระบบจะค้นหาข้อมูลจาก Wikipedia ทั้งใน
- ด้านบวก (Achievements)
- ด้านลบ (Criticism / Controversy)
จากนั้นใช้ Agent ที่ทำหน้าที่เป็น “ผู้พิพากษา” เพื่อประเมินความสมดุลของข้อมูล และสร้างรายงานที่เป็นกลางที่สุด
ผลลัพธ์สุดท้ายจะถูกบันทึกเป็นไฟล์ ้historical_court.txt

Objectives
1. ใช้ Multi-Agent Architecture
2. วิเคราะห์ข้อมูลจากหลายมุมมอง
3. สร้างรายงานที่เป็นกลาง
4. ใช้ Wikipedia เป็นแหล่งข้อมูล
5. ใช้ Loop mechanism เพื่อปรับปรุงข้อมูลจนสมบูรณ์

ระบบประกอบด้วย 4 ขั้นตอนหลัก

Step 1: Inquiry (Sequential)
Step 2: Investigation (Parallel)
Step 3: Trial & Review (Loop)
Step 4: Verdict (Output)

Agent Description
1. Root Agent (Inquiry Agent)

หน้าที่:
รับ input จาก User
เก็บข้อมูลใน state: PROMPT
เริ่ม workflow

2. Investigation Team (Parallel Agents)
ทำงานแบบ Parallel เพื่อรวบรวมข้อมูลสองด้าน ด้านบวก และ ลบ

2.1 Admirer Agent
บทบาท: ฝ่ายสนับสนุน
หน้าที่:
ค้นหาด้านบวก ,achievements ,success ,legacy
และจะบันทึกในไว้ใน
pos_data

2.2 Critic Agent
บทบาท: ฝ่ายกล่าวหา
หน้าที่:
ค้นหาด้านลบ
controversy
criticism
failures

และจะบันทึกข้อมูลไว้ใน
neg_data

Trial Loop
Loop นี้จะทำงานจนกว่าข้อมูลจะสมบูรณ์

ประกอบด้วย 3 Agent

3.1 Admirer Loop Agent

หน้าที่:
เพิ่มข้อมูลด้านบวกตาม feedback จาก Judge

3.2 Critic Loop Agent

หน้าที่:
เพิ่มข้อมูลด้านลบตาม feedback จาก Judge

3.3 Judge Agent

บทบาท: ผู้พิพากษา
หน้าที่:
ตรวจสอบความสมดุลของข้อมูล

ถ้าไม่สมดุล:

append_to_state → judge_feedback

ถ้าสมดุล:

exit_loop

4. Verdict Agent

หน้าที่:
สร้างรายงานที่เป็นกลาง
รวมข้อมูลด้านบวกและด้านลบ
บันทึกไฟล์ใน historical_court.txt

Output:

historical_court/{PROMPT}.txt
