from PIL import Image

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
    row = Image.new("RGB", (len(temp_bits) * TILE_W, TILE_H))
    for i, bit in enumerate(temp_bits):
        row.paste(tile_map[bit], (i * TILE_W, 0))
    return row


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

frames = [] 


for i in range(int("11", 2) + 1):

    bits = list(f"{i:02b}")
    room_state = ["clean" if bit == "0" else "dirty" for bit in bits]
    
    for j in range(len(bits)):

        print(f"\n State " + str(state) + ":")
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

        frames.append(draw_state_image(temp_bits))

        print("".join(temp_bits))

        for k in range(len(bits)):
            print(f"Room {room_num[k]} is {room_state[k]}")
        
        print("VC in room " + str(j + 1))
        print("If goal is reached:\n   stop\nelse:")
        print("   [" + ", ".join(steps) + "]")
        steps.clear()

frames[0].save("vacuum_states.pdf", save_all=True, append_images=frames[1:])
print("\nAll states have been saved to vacuum_states.pdf")