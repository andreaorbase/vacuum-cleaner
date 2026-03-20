from PIL import Image
import io
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

room_num = ['A', 'B', 'C', 'D', 'E']
state = 1
steps = []

tile_map = {
    "0": Image.open("src/clean.png"),
    "1": Image.open("src/dirty.png"),
    "2": Image.open("src/vacuum_clean.png"),
    "3": Image.open("src/vacuum_dirty.png")
}
TILE_W, TILE_H = tile_map["0"].size

def draw_state_image(temp_bits):
    scaled_w = TILE_W // 2
    scaled_h = TILE_H // 2
    row = Image.new("RGB", (len(temp_bits) * scaled_w, scaled_h))
    for i, bit in enumerate(temp_bits):
        tile = tile_map[bit].resize((scaled_w, scaled_h))
        row.paste(tile, (i * scaled_w, 0))
    return row

def write_page(c, state_num, img, room_labels, vc_room, steps_list):
    page_w, page_h = custom_size
    y = page_h - 50  # start from top

    # state number
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"State {state_num}:")
    y -= 30

    # grid image
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_w = len(room_labels) * (TILE_W // 2)
    img_h = TILE_H // 2
    c.drawImage(ImageReader(img_buffer), 50, y - img_h, width=img_w, height=img_h)
    y -= img_h + 20

    # room states and vc position
    c.setFont("Helvetica", 12)
    for label in room_labels:
        c.drawString(50, y, label)
        y -= 20

    c.drawString(50, y, f"VC in room {vc_room}")
    y -= 20

    # steps
    c.drawString(50, y, "If goal is reached:")
    y -= 20
    c.drawString(70, y, "stop")
    y -= 20
    c.drawString(50, y, "else:")
    y -= 20
    if steps_list:
        c.drawString(70, y, "[" + ", ".join(steps_list) + "]")
    else:
        c.drawString(70, y, "[]")

    c.showPage()  # end of this page


def move_left():
    steps.append("Left")

def move_right():
    steps.append("Right")

def suck():
    steps.append("Suck")


def start_cleaning(num_lr, num_rr, v_pos, list_lr, list_rr, bits):

    if bits[v_pos] == "1":
        suck()
        bits[v_pos] = "0"
        if v_pos in list_lr:
            list_lr.remove(v_pos)
        elif v_pos in list_rr:
            list_rr.remove(v_pos)

    if num_lr < num_rr or num_lr == num_rr:
        if list_lr:
            farthest_left = min(list_lr)
            while v_pos > farthest_left:
                    move_left()
                    v_pos -= 1
                    if v_pos in list_lr:
                        suck()
                        list_lr.remove(v_pos)

        if list_rr:
            farthest_right = max(list_rr)
            while v_pos < farthest_right:
                move_right()
                v_pos += 1
                if v_pos in list_rr:
                    suck()
                    list_rr.remove(v_pos)
    else:
        if list_rr:
            farthest_right = max(list_rr)
            while v_pos < farthest_right:
                move_right()
                v_pos += 1
                if v_pos in list_rr:
                    suck()
                    list_rr.remove(v_pos)
        if list_lr:
            farthest_left = min(list_lr)
            while v_pos > farthest_left:
                    move_left()
                    v_pos -= 1
                    if v_pos in list_lr:
                        suck()
                        list_lr.remove(v_pos)          


from reportlab.lib.pagesizes import A4
custom_size = (A4[0] * 2/3, A4[1] * 1/2)
pdf = canvas.Canvas("Orbase_Assignment_Vaccum-World.pdf", pagesize=custom_size)


for i in range(int("11111", 2) + 1):

    bits = list(f"{i:05b}")
    room_state = ["clean" if bit == "0" else "dirty" for bit in bits]
    
    for j in range(len(bits)):

        print(f"\n State " + str(state) + ":")
        current_state = state
        state += 1
        
        temp_bits = bits.copy()
        if bits[j] == "1":
            temp_bits[j] = "3" # dirty room with VC
        else:
            temp_bits[j] = "2" # clean room with VC
        
        left_dirty_rooms = [idx for idx, bit in enumerate(bits) if bit == "1" and idx < j]
        right_dirty_rooms = [idx for idx, bit in enumerate(bits) if bit == "1" and idx > j]

        num_left_rooms = len(left_dirty_rooms)
        num_right_rooms = len(right_dirty_rooms)
        
        bits_copy = bits.copy()
        start_cleaning(num_left_rooms, num_right_rooms, j, left_dirty_rooms, right_dirty_rooms, bits_copy)
        img = draw_state_image(temp_bits)

        # room label strings
        room_labels = [f"Room {room_num[k]} is {room_state[k]}" for k in range(len(bits))]

        # write everything to one PDF page
        write_page(pdf, current_state, img, room_labels, j + 1, steps)

        # keep your console prints if you want
        print(f"\n State {current_state}:")
        print("".join(temp_bits))
        for k in range(len(bits)):
            print(f"Room {room_num[k]} is {room_state[k]}")
        print("VC in room " + str(j + 1))
        print("If goal is reached:\n   stop\nelse:")
        print("   [" + ", ".join(steps) + "]")
        
        steps.clear()

pdf.save()
print("\nStates have been saved as pdf!")