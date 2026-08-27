import re

# Questions database.
# Each question contains:
# - id: unique string
# - title: section title
# - type: 'choice', 'input-set', 'input-interval', 'input-inequality'
# - story: setting the scene
# - enemy: name of the enemy beast
# - enemy_max_hp: HP of the enemy
# - question_text: math question
# - hint: a small hint
# - explanation: step-by-step mathematical solution (in Thai)
# - acceptable_answers: list of regexes or values used for verification
# - visual_type: helper for drawing the graph/mapping on canvas ('ordered-pairs', 'mapping', 'discrete-graph', 'continuous-graph', 'algebraic')
# - visual_data: dictionary containing parameters for JS rendering

QUESTIONS = [
    # ==================== STAGE 1: FOREST OF ORDERED PAIRS ====================
    {
        "id": "s1_q1",
        "stage": 1,
        "title": "ด่านที่ 1: ป่าคู่ระเบียบ - ผู้เฝ้าประตูไม้โบราณ",
        "enemy": "อสูรไม้เบิร์ช (Birch Golem)",
        "enemy_max_hp": 100,
        "story": "คุณเดินเข้ามาในป่าลึก พบกับอสูรร่างไม้โบราณที่สลักความสัมพันธ์ไว้บนตัว มันพูดว่า: 'หากจะผ่านไป จงหาขอบเขตของข้อมูลนำเข้า (โดเมน) ของข้า!'",
        "question_text": "กำหนดความสัมพันธ์ R = {(1, 2), (3, 4), (5, 6)}\nจงหา โดเมน (Domain) ของความสัมพันธ์นี้",
        "hint": "โดเมนคือเซตของสมาชิกตัวหน้าของทุกคู่ระเบียบ เขียนตัวเลขคั่นด้วยจุลภาค (เช่น 1, 2, 3)",
        "explanation": "โดเมน (Domain) คือเซตของสมาชิกตัวหน้าของคู่ระเบียบทั้งหมดในความสัมพันธ์\n"
                      "จาก R = {"จาก R = {(1, 2), (3, 4), (5, 6)}\n"
                      "สมาชิกตัวหน้าคือ 1, 3, 5\n"
                      "ดังนั้น โดเมนคือ {1, 3, 5}",
        "type": "input-set",
        "acceptable_answers": ["1,3,5", "{1,3,5}", "1, 3, 5", "{1, 3, 5}"],
        "visual_type": "ordered-pairs",
        "visual_data": {
            "pairs": [[1, 2], [3, 4], [5, 6]]
        }
    },
    {
        "id": "s1_q2",
        "stage": 1,
        "title": "ด่านที่ 1: ป่าคู่ระเบียบ - ปลักโคลนแห่งความซ้ำ",
        "enemy": "สไลม์โคลนตม (Mud Slime)",
        "enemy_max_hp": 100,
        "story": "สไลม์โคลนขวางทางน้ำไหลไว้ มันมีชุดคู่ระเบียบที่สลับซับซ้อนและมีตัวเลขซ้ำกันร่ายล้อม: 'จงบอกขอบเขตผลลัพธ์ (เรนจ์) ของข้า! อย่าลืมกฎของเซตล่ะ!'",
        "question_text": "กำหนดความสัมพันธ์ R = {(-1, 8), (0, 0), (2, -4), (5, 8)}\nจงหา เรนจ์ (Range) ของความสัมพันธ์นี้",
        "hint": "เรนจ์คือเซตของสมาชิกตัวหลัง ในเซตหากมีสมาชิกซ้ำกัน ให้เขียนเพียงครั้งเดียวเท่านั้น เรียงลำดับจากน้อยไปมาก (เช่น -4, 0, 8)",
        "explanation": "เรนจ์ (Range) คือเซตของสมาชิกตัวหลังของคู่ระเบียบทั้งหมด\n"
                      "จาก R = {(-1, \x1b[36m8\x1b[0m), (0, \x1b[36m0\x1b[0m), (2, \x1b[36m-4\x1b[0m), (5, \x1b[36m8\x1b[0m)}\n"
                      "สมาชิกตัวหลังคือ 8, 0, -4, 8\n"
                      "เนื่องจากเลข 8 ซ้ำกัน ในเซตเราจะเขียนเพียงครั้งเดียว\n"
                      "ดังนั้น เรนจ์คือ {-4, 0, 8}",
        "type": "input-set",
        "acceptable_answers": ["-4,0,8", "{-4,0,8}", "-4, 0, 8", "{-4, 0, 8}", "8,0,-4"],
        "visual_type": "ordered-pairs",
        "visual_data": {
            "pairs": [[-1, 8], [0, 0], [2, -4], [5, 8]]
        }
    },
    {
        "id": "s1_q3",
        "stage": 1,
        "title": "ด่านที่ 1: ป่าคู่ระเบียบ - ศาลเจ้าแห่งแผนภาพ",
        "enemy": "วิญญาณผู้พิทักษ์ลูกศร (Arrow Spirit)",
        "enemy_max_hp": 100,
        "story": "หน้าประตูศาลเจ้า มีแผนภาพลูกศรชี้จากเซต A ไปยังเซต B โดดเด่นขึ้นมา วิญญาณผู้พิทักษ์กล่าวว่า: 'ไม่ใช่ทุกอย่างในดินแดนปลายทางที่จะถูกเลือก จงหาค่าเรนจ์ที่แท้จริง!'",
        "question_text": "กำหนดแผนภาพการจับคู่จากเซต A = {a, b, c} ไปยัง B = {x, y, z}\nโดยมีเงื่อนไข: a จับคู่กับ x, b จับคู่กับ y, และ c จับคู่กับ y\nจงหา เรนจ์ (Range) ของความสัมพันธ์นี้",
        "hint": "เรนจ์คือเซตของสมาชิกปลายทาง (ในเซต B) ที่มีลูกศรชี้ไปหาเท่านั้น ตัวใดที่ไม่มีลูกศรชี้ไปหาจะไม่ใช่เรนจ์ (ตอบคั่นด้วยจุลภาค เช่น x, y)",
        "explanation": "เรนจ์คือเซตของสมาชิกปลายทางที่มีความสัมพันธ์จริง (มีลูกศรชี้ไปถึง)\n"
                      "ในข้อนี้:\n"
                      " - a ชี้ไปหา x (x เป็นเรนจ์)\n"
                      " - b ชี้ไปหา y (y เป็นเรนจ์)\n"
                      " - c ชี้ไปหา y\n"
                      " - z ไม่มีลูกศรชี้ไปหาเลย (ดังนั้น z ไม่ใช่เรนจ์)\n"
                      "ดังนั้น เรนจ์คือ {x, y}",
        "type": "input-set",
        "acceptable_answers": ["x,y", "{x,y}", "x, y", "{x, y}", "y,x"],
        "visual_type": "mapping",
        "visual_data": {
            "domain_set": ["a", "b", "c"],
            "codomain_set": ["x", "y", "z"],
            "mappings": [["a", "x"], ["b", "y"], ["c", "y"]]
        }
    },

    # ==================== STAGE 2: GROTTO OF GRAPHS ====================
    {
        "id": "s2_q1",
        "stage": 2,
        "title": "ด่านที่ 2: ถ้ำใต้พิภพแห่งกราฟ - ผู้อัญเชิญพิกัด",
        "enemy": "ยักษ์หินออบซิเดียน (Obsidian Golem)",
        "enemy_max_hp": 100,
        "story": "เมื่อเดินเข้าสู่ถ้ำมืด พลันปรากฏแกนพิกัดฉากและจุดไฟสว่างวาบบนผนังถ้ำ ยักษ์หินทุบกระบองท้าทาย: 'จงอ่านค่าแกนนอนของจุดเหล่านี้เพื่อสร้างโดเมนซะ!'",
        "question_text": "จากกราฟที่เป็นจุดพิกัดในระบบพิกัดฉาก 4 จุด ดังนี้:\n(-2, 1), (0, 3), (2, 5), (4, 1)\nจงหา โดเมน (Domain) ของกราฟนี้",
        "hint": "บนกราฟแกน x และ y โดเมนให้อ่านค่าพิกัดตัวแรก (ตามแกน x) ของจุดทุกจุดมารวมกันเป็นเซต (ตอบคั่นด้วยจุลภาค เช่น -2, 0, 2, 4)",
        "explanation": "เมื่อกราฟประกอบด้วยจุดตัดที่ไม่ต่อเนื่องกัน โดเมนก็คือเซตของพิกัด x ของจุดเหล่านั้น\n"
                      "จุดทั้งสี่มีพิกัดคือ (\x1b[33m-2\x1b[0m, 1), (\x1b[33m0\x1b[0m, 3), (\x1b[33m2\x1b[0m, 5), (\x1b[33m4\x1b[0m, 1)\n"
                      "พิกัด x ได้แก่ -2, 0, 2, 4\n"
                      "ดังนั้น โดเมนคือ {-2, 0, 2, 4}",
        "type": "input-set",
        "acceptable_answers": ["-2,0,2,4", "{-2,0,2,4}", "-2, 0, 2, 4", "{-2, 0, 2, 4}"],
        "visual_type": "discrete-graph",
        "visual_data": {
            "points": [[-2, 1], [0, 3], [2, 5], [4, 1]]
        }
    },
    {
        "id": "s2_q2",
        "stage": 2,
        "title": "ด่านที่ 2: ถ้ำใต้พิภพแห่งกราฟ - สะพานแห่งความต่อเนื่อง",
        "enemy": "ค้างคาวคริสตัล (Crystal Bat)",
        "enemy_max_hp": 100,
        "story": "สะพานหินถูกตัดขาด แต่มีแสงเลเซอร์สีฟ้าเชื่อมต่อกันเป็นเส้นตรงยาวจากซ้ายไปขวา ค้างคาวคริสตัลบินร่อนเข้ามา: 'เลเซอร์นี้มีจุดสิ้นสุดเป็นวงทึบทั้งสองฝั่ง โดเมนที่ครอบคลุมคือช่วงใด?'",
        "question_text": "กราฟบนแกนพิกัดฉากเป็นส่วนของเส้นตรงที่เชื่อมระหว่างจุด (-3, -1) และ (4, 3) โดยจุดปลายทั้งสองเป็นวงกลมทึบ (Closed Circle)\nจงหา โดเมน (Domain) ในรูปช่วง (Interval Notation)",
        "hint": "เนื่องจากกราฟต่อเนื่อง โดเมนคือช่วงของ x ตั้งแต่ค่าซ้ายสุดไปขวาสุด วงกลมทึบหมายถึงรวมจุดนั้นด้วย ใช้สัญลักษณ์วงเล็บเหลี่ยม [...] เช่น [-3, 4]",
        "explanation": "เนื่องจากกราฟเป็นเส้นต่อเนื่อง โดเมนจึงต้องบอกขอบเขตค่า x เป็นช่วง (Interval)\n"
                      "1. มองไปที่แกน x: กราฟเริ่มตั้งแต่ x = -3 ทางซ้าย ไปจนถึง x = 4 ทางขวา\n"
                      "2. จุดปลายทั้งสองเป็นวงทึบ (ทึบ = รวมค่าปลาย) หมายความว่า -3 <= x <= 4\n"
                      "3. เขียนในสัญกรณ์ช่วงได้เป็น [-3, 4]",
        "type": "input-interval",
        "acceptable_answers": ["[-3,4]", "[-3, 4]", "-3<=x<=4", "-3 <= x <= 4"],
        "visual_type": "continuous-graph",
        "visual_data": {
            "start": [-3, -1, True],  # [x, y, is_closed]
            "end": [4, 3, True],
            "type": "line"
        }
    },
    {
        "id": "s2_q3",
        "stage": 2,
        "title": "ด่านที่ 2: ถ้ำใต้พิภพแห่งกราฟ - ห้องกระจกเงาหัวกลับ",
        "enemy": "แมงมุมมิติกระจก (Mirror Spider)",
        "enemy_max_hp": 120,
        "story": "ผนังถ้ำเต็มไปด้วยกระจกเงา สะท้อนเส้นโค้งเลเซอร์แปลกๆ มีวงทึบที่จุดล่างสุด และวงโปร่งที่จุดบนสุด แมงมุมพ่นใย: 'คราวนี้ต้องหาขอบเขตของผลลัพธ์ในแกนตั้ง (เรนจ์) บอกข้าที!'",
        "question_text": "กราฟเป็นเส้นโค้งที่เริ่มจากจุดต่ำสุดที่ (0, 0) ซึ่งเป็นวงกลมทึบ ไปสิ้นสุดที่จุดสูงสุดที่ (4, 2) ซึ่งเป็นวงกลมโปร่ง (Open Circle)\nจงหา เรนจ์ (Range) ของกราฟนี้ในรูปช่วง (Interval Notation)",
        "hint": "เรนจ์คือช่วงในแกน y ตั้งแต่ค่าต่ำสุด (ล่างสุด) ไปยังค่าสูงสุด (บนสุด) วงกลมโปร่งหมายถึงไม่รวมค่าปลายนั้น ให้ใช้วงเล็บโค้ง ) เช่น [0, 2)",
        "explanation": "เรนจ์บอกช่วงของแกน y (ระดับความสูงต่ำของกราฟ)\n"
                      "1. มองที่แกน y: กราฟต่ำสุดอยู่ที่ y = 0 และสูงสุดอยู่ที่ y = 2\n"
                      "2. จุดต่ำสุด (0, 0) เป็นวงกลมทึบ รวม y = 0 ด้วย (ใช้ [ )\n"
                      "3. จุดสูงสุด (4, 2) เป็นวงกลมโปร่ง ไม่รวม y = 2 (ใช้ ) )\n"
                      "4. ช่วงของแกน y คือ 0 <= y < 2 หรือเขียนเป็นสัญกรณ์ช่วงได้ว่า [0, 2)",
        "type": "input-interval",
        "acceptable_answers": ["[0,2)", "[0, 2)", "0<=y<2", "0 <= y < 2"],
        "visual_type": "continuous-graph",
        "visual_data": {
            "start": [0, 0, True],
            "end": [4, 2, False],
            "type": "curve"
        }
    },

    # ==================== STAGE 3: FORTRESS OF FUNCTIONS ====================
    {
        "id": "s3_q1",
        "stage": 3,
        "title": "ด่านที่ 3: ปราสาทแห่งฟังก์ชัน - ภัยคุกคามของเศษส่วน",
        "enemy": "โกเลมศิลาต้องห้าม (Forbidden Rune Golem)",
        "enemy_max_hp": 120,
        "story": "ในตัวปราสาท มีแผ่นหินจารึกฟังก์ชันเศษส่วนลอยอยู่กลางอากาศ โกเลมผู้เฝ้าห้องทักทาย: 'กฎเหล็กของคณิตศาสตร์คือห้ามหารด้วยศูนย์! จงหาว่าค่า x ใดที่ถูกห้ามในโดเมนนี้!'",
        "question_text": "กำหนดฟังก์ชัน f(x) = 5 / (x - 3)\nจงหาโดเมนของฟังก์ชันนี้ (ตอบเงื่อนไขของ x เช่น x != 3)",
        "hint": "ส่วนของเศษส่วนห้ามเป็น 0 เด็ดขาด ดังนั้นตัวส่วน x - 3 ต้องไม่เท่ากับ 0 แก้สมการหาค่า x ที่ทำให้ตัวส่วนเป็นศูนย์แล้วตอบในรูป x != ค่าตัวเลข",
        "explanation": "ในฟังก์ชันเศษส่วน ตัวส่วนจะต้องไม่เท่ากับ 0 เสมอ\n"
                      "จาก f(x) = 5 / (x - 3) จะได้เงื่อนไข:\n"
                      "   x - 3 != 0\n"
                      "   x != 3\n"
                      "ดังนั้น โดเมนของฟังก์ชันนี้คือ เซตของจำนวนจริงทั้งหมดยกเว้น 3 หรือเขียนว่า x != 3",
        "type": "input-inequality",
        "acceptable_answers": ["x!=3", "x != 3", "x!==3", "x !== 3", "R-{3}", "R - {3}"],
        "visual_type": "algebraic",
        "visual_data": {
            "expression": "f(x) = \\frac{5}{x - 3}"
        }
    },
    {
        "id": "s3_q2",
        "stage": 3,
        "title": "ด่านที่ 3: ปราสาทแห่งฟังก์ชัน - ผู้คุมกฎรากที่สอง",
        "enemy": "ไวเวิร์นน้ำแข็ง (Frost Wyvern)",
        "enemy_max_hp": 150,
        "story": "ไวเวิร์นน้ำแข็งคำรามพ่นไอเย็นยะเยือก ปรากฏสมการติดรูทขึ้นมา: 'ในทางจำนวนจริง ค่าใต้รากที่สองห้ามติดลบเด็ดขาด! โดเมนของข้าต้องมีค่าตั้งแต่เท่าไหร่ขึ้นไป?'",
        "question_text": "กำหนดฟังก์ชัน f(x) = sqrt(x - 2) หรือ f(x) = √(x - 2)\nจงหาโดเมนของฟังก์ชันนี้ (ตอบเงื่อนไขของ x ในรูปอสมการ เช่น x >= 2)",
        "hint": "ค่าภายใต้เครื่องหมายรากที่สอง (Square Root) ต้องมากกว่าหรือเท่ากับ 0 เสมอ ตั้งอสมการ x - 2 >= 0 แล้วแก้สมการหาคำตอบ",
        "explanation": "ภายใต้เครื่องหมายรากที่สองในระบบจำนวนจริง ค่าข้างในห้ามติดลบ\n"
                      "ดังนั้น x - 2 ต้องมากกว่าหรือเท่ากับ 0\n"
                      "เขียนอสมการ: x - 2 >= 0\n"
                      "แก้ขอบเขตได้: x >= 2\n"
                      "ดังนั้น โดเมนคือ x >= 2 (หรือช่วง [2, infinity))",
        "type": "input-inequality",
        "acceptable_answers": ["x>=2", "x >= 2", "[2,inf)", "[2, inf)", "[2, infinity)"],
        "visual_type": "algebraic",
        "visual_data": {
            "expression": "f(x) = \\sqrt{x - 2}"
        }
    },
    {
        "id": "s3_q3",
        "stage": 3,
        "title": "ด่านที่ 3: ปราสาทแห่งฟังก์ชัน - ศิลาขอบเขตผลลัพธ์",
        "enemy": "จอมเวททึมทึบ (Archmage Void)",
        "enemy_max_hp": 180,
        "story": "บอสใหญ่เฝ้าประตูห้องคลังสมบัติ ปรากฏฟังก์ชันยกกำลังสองขึ้นมา: 'ค่าผลลัพธ์ที่เกิดจากการยกกำลังสองย่อมไม่มีทางเป็นลบ! จงหาขอบเขตของผลลัพธ์ (เรนจ์ y) ที่เป็นไปได้ทั้งหมดของสมการนี้!'",
        "question_text": "กำหนดฟังก์ชัน f(x) = x^2 + 4\nจงหาเรนจ์ (Range) ของฟังก์ชันนี้ (ตอบเงื่อนไขของ y หรือ f(x) เช่น y >= 4)",
        "hint": "เนื่องจาก x^2 มีค่าอย่างต่ำที่สุดคือ 0 เสมอ (ไม่มีทางติดลบ) ดังนั้นค่าที่ต่ำที่สุดของ x^2 + 4 จะเป็นเท่าใด? ตอบในรูปอสมการของ y (เช่น y >= 4)",
        "explanation": "หาเรนจ์ (ค่า y หรือ f(x) ที่เป็นไปได้ทั้งหมด):\n"
                      "เนื่องจากสัญกรณ์ยกกำลังสองของจำนวนจริง x^2 >= 0 เสมอ สำหรับทุกจำนวนจริง x\n"
                      "เมื่อเราบวก 4 ทั้งสองข้าง:\n"
                      "   x^2 + 4 >= 0 + 4\n"
                      "   f(x) >= 4 หรือ y >= 4\n"
                      "ดังนั้น ค่า y ที่เป็นไปได้ทั้งหมดคือตั้งแต่ 4 ขึ้นไป\n"
                      "เขียนได้ว่า y >= 4 (หรือช่วง [4, infinity))",
        "type": "input-inequality",
        "acceptable_answers": ["y>=4", "y >= 4", "f(x)>=4", "f(x) >= 4", "[4,inf)", "[4, inf)"],
        "visual_type": "algebraic",
        "visual_data": {
            "expression": "f(x) = x^2 + 4"
        }
    }
]

def clean_input(user_str: str) -> str:
    """Normalizes whitespace and common formatting characters."""
    if not user_str:
        return ""
    # Remove spaces
    s = user_str.replace(" ", "")
    # Normalize inequalities
    s = s.replace(">=", "≥").replace("<=", "≤").replace("!=", "≠")
    # Normalize brackets/curly braces
    s = s.replace("{", "").replace("}", "")
    # Lowercase
    s = s.lower()
    return s

def check_answer(question_id: str, user_answer: str) -> bool:
    """
    Validates user_answer against correct answers for the question.
    Handles set representations, intervals, and inequalities robustly.
    """
    # Find the question
    question = next((q for q in QUESTIONS if q["id"] == question_id), None)
    if not question:
        return False

    cleaned_user = clean_input(user_answer)
    
    # Check against list of acceptable answers
    for acceptable in question["acceptable_answers"]:
        cleaned_acc = clean_input(acceptable)
        
        # Exact match of normalized strings
        if cleaned_user == cleaned_acc:
            return True
            
        # Set comparison: if it is a list of items separated by commas, compare as sets
        if "," in cleaned_acc and "," in cleaned_user:
            user_set = set(cleaned_user.split(","))
            acc_set = set(cleaned_acc.split(","))
            if user_set == acc_set:
                return True

    # Fallback to smart parsing for intervals and inequalities
    if question["type"] == "input-interval":
        # Match something like [-3,4] or [-3, 4]
        # Clean user input by removing extra brackets or spaces
        u_match = re.match(r"^[\[\()](-?\d+),(-?\d+)[\]\)]$", cleaned_user)
        for acceptable in question["acceptable_answers"]:
            a_match = re.match(r"^[\[\()](-?\d+),(-?\d+)[\]\)]$", clean_input(acceptable))
            if u_match and a_match:
                # Check bounds and inclusion brackets
                u_bracket_start, u_val1, u_val2, u_bracket_end = cleaned_user[0], u_match.group(1), u_match.group(2), cleaned_user[-1]
                a_bracket_start, a_val1, a_val2, a_bracket_end = clean_input(acceptable)[0], a_match.group(1), a_match.group(2), clean_input(acceptable)[-1]
                if u_val1 == a_val1 and u_val2 == a_val2 and u_bracket_start == a_bracket_start and u_bracket_end == a_bracket_end:
                    return True
                    
        # Check if the user wrote it as an inequality, like -3<=x<=4 or 0<=y<2
        # Translate to interval and check. 
        # For simplicity, we also added inequality formats directly to the acceptable answers of interval questions!

    elif question["type"] == "input-inequality":
        # E.g. x!=3 or x>=2 or y>=4
        # We replace symbols and check equality
        cleaned_user_std = cleaned_user.replace("≠", "!=").replace("≥", ">=").replace("≤", "<=")
        for acceptable in question["acceptable_answers"]:
            cleaned_acc_std = clean_input(acceptable).replace("≠", "!=").replace("≥", ">=").replace("≤", "<=")
            if cleaned_user_std == cleaned_acc_std:
                return True
                
    return False