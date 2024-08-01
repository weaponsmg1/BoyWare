import tkinter as tk
import pyMeow as pm

class Loader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BoyWare Loader")
        self.geometry("300x150")
        self.configure(bg="black")  
        self.resizable(False, False)

        label = tk.Label(self, text="BoyWare", font=("Arial", 24), fg="red", bg="black")
        label.pack(pady=20)

        start_button = tk.Button(self, text="Assault Cube", command=self.start_main, bg="white", fg="black")
        start_button.pack(pady=10)

    def start_main(self):
        self.destroy()  
        main()  

def main():
    proc = pm.open_process("ac_client.exe")
    base = pm.get_module(proc, "ac_client.exe")["base"]

    class pointer:
        player_count = 0x18AC0C
        entity_list = 0x18AC04
        local_player = 0x18AC00
        view_matrix = 0x17DFD0

    class offsets:
        name = 0x205
        health = 0xEC
        armor = 0xF0
        team = 0x30C
        pos = 0x4
        fpos = 0x28

    class colors:
        blue = pm.get_color("blue")
        red = pm.get_color("red")
        white = pm.get_color("white")
        green = pm.get_color("green")
        dark_red = pm.get_color("dark_red")
        dark_blue = pm.get_color("dark_blue")
        crosshair_color = pm.get_color("cyan")
        label_color = pm.get_color("red")

    class function:
        def __init__(self, addr):
            self.addr = addr
            self.health = pm.r_int(proc, addr + offsets.health)
            if self.health <= 0:
                raise Exception("Entity is not alive.")
            self.name = pm.r_string(proc, addr + offsets.name)
            self.armor = pm.r_int(proc, addr + offsets.armor)
            self.team = pm.r_int(proc, addr + offsets.team)
            self.color = colors.blue if self.team else colors.red
            self.pos3d = pm.r_vec3(proc, self.addr + offsets.pos)
            self.fpos3d = pm.r_vec3(proc, self.addr + offsets.fpos)
            self.pos2d = self.fpos2d = None
            self.head = self.width = self.center = None

        def wts(self, vm):
            try:
                self.pos2d = pm.world_to_screen(vm, self.pos3d)
                self.fpos2d = pm.world_to_screen(vm, self.fpos3d)
                self.head = self.fpos2d["y"] - self.pos2d["y"]
                self.width = self.head / 2
                self.center = self.width / 2
                return True
            except:
                return False

        def draw_box(self):
            pm.draw_rectangle(
                posX=self.pos2d["x"] - self.center,
                posY=self.pos2d["y"] - self.center / 2,
                width=self.width,
                height=self.head + self.center / 2,
                color=pm.fade_color(self.color, 0.3),
            )
            pm.draw_rectangle_lines(
                posX=self.pos2d["x"] - self.center,
                posY=self.pos2d["y"] - self.center / 2,
                width=self.width,
                height=self.head + self.center / 2,
                color=self.color,
                lineThick=1.2,
            )

        def draw_name(self):
            textSize = pm.measure_text(self.name, 15) / 2
            pm.draw_text(
                text=self.name,
                posX=self.pos2d["x"] - textSize,
                posY=self.pos2d["y"] - self.head / 2 - 15,
                fontSize=15,
                color=colors.white,
            )

            bar_width = 5
            bar_height = self.head
            health_percentage = self.health / 100
            filled_height = bar_height * health_percentage
            pm.draw_rectangle(
                posX=self.pos2d["x"] - self.center - bar_width - 10,
                posY=self.pos2d["y"] - self.center / 2,
                width=bar_width,
                height=bar_height,
                color=colors.dark_red,
            )
            pm.draw_rectangle(
                posX=self.pos2d["x"] - self.center - bar_width - 10,
                posY=self.pos2d["y"] - self.center / 2 + (bar_height - filled_height),
                width=bar_width,
                height=filled_height,
                color=colors.green,
            )

            armor_bar_width = 5
            armor_bar_height = self.head
            armor_percentage = self.armor / 100
            armor_filled_height = armor_bar_height * armor_percentage
            pm.draw_rectangle(
                posX=self.pos2d["x"] + self.center + 10,
                posY=self.pos2d["y"] - self.center / 2,
                width=armor_bar_width,
                height=armor_bar_height,
                color=colors.dark_blue,
            )
            pm.draw_rectangle(
                posX=self.pos2d["x"] + self.center + 10,
                posY=self.pos2d["y"] - self.center / 2 + (armor_bar_height - armor_filled_height),
                width=armor_bar_width,
                height=armor_filled_height,
                color=colors.blue,
            )

    def draw_crosshair():
        screen_width = pm.get_screen_width()
        screen_height = pm.get_screen_height()
        crosshair_size = 10
        crosshair_thickness = 2
        crosshair_color = colors.crosshair_color

        pm.draw_line(
            startPosX=screen_width / 2 - crosshair_size,
            startPosY=screen_height / 2,
            endPosX=screen_width / 2 + crosshair_size,
            endPosY=screen_height / 2,
            color=crosshair_color,
        )
        pm.draw_line(
            startPosX=screen_width / 2,
            startPosY=screen_height / 2 - crosshair_size,
            endPosX=screen_width / 2,
            endPosY=screen_height / 2 + crosshair_size,
            color=crosshair_color,
        )

    pm.overlay_init(target="AssaultCube", trackTarget=True)
    while pm.overlay_loop():
        pm.begin_drawing()
        player_count = pm.r_int(proc, base + pointer.player_count)
        if player_count > 1:
            ent_buffer = pm.r_ints(
                proc, pm.r_int(proc, base + pointer.entity_list), player_count
            )[1:]
            v_matrix = pm.r_floats(proc, base + pointer.view_matrix, 16)
            for addr in ent_buffer:
                try:
                    ent = function(addr)
                    if ent.wts(v_matrix):
                        ent.draw_box()
                        ent.draw_name()
                except:
                    continue
        draw_crosshair()

        screen_width = pm.get_screen_width()
        pm.draw_text(
            text="BoyWare",
            posX=screen_width - pm.measure_text("BoyWare", 20) - 10,
            posY=10,
            fontSize=20,
            color=colors.label_color,
        )

        pm.end_drawing()

if __name__ == "__main__":
    loader = Loader()
    loader.mainloop()
