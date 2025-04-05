import tkinter as tk
import math
import random

canvas_width = 800
canvas_height = 600
scale = 200
center_x = canvas_width / 2
center_y = canvas_height / 2
dt = 0.02           # Time step (seconds)

theta_x = 0.0
theta_y = 0.0
theta_z = 0.0
omega_x = 0.0
omega_y = 0.0
omega_z = 0.0

stabilizing = False
aligning = False
laser_timer = 0 

target_angle = math.radians(45)  # 45° target for x, y, and z
tolerance = math.radians(5)      # 5° tolerance

cube_vertices = [
    (-0.5, -0.5, -0.5),
    ( 0.5, -0.5, -0.5),
    ( 0.5,  0.5, -0.5),
    (-0.5,  0.5, -0.5),
    (-0.5, -0.5,  0.5),
    ( 0.5, -0.5,  0.5),
    ( 0.5,  0.5,  0.5),
    (-0.5,  0.5,  0.5),
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

num_stars = 150
stars = []
for _ in range(num_stars):
    x = random.randint(0, canvas_width)
    y = random.randint(0, canvas_height)
    stars.append((x, y))

def rotate_point(x, y, z):
    y, z = y * math.cos(theta_x) - z * math.sin(theta_x), y * math.sin(theta_x) + z * math.cos(theta_x)
    x, z = x * math.cos(theta_y) + z * math.sin(theta_y), -x * math.sin(theta_y) + z * math.cos(theta_y)
    x, y = x * math.cos(theta_z) - y * math.sin(theta_z), x * math.sin(theta_z) + y * math.cos(theta_z)
    return x, y, z

def project_point(x, y, z):
    f = 200
    factor = f / (f + z) if (f + z) != 0 else 1
    x2d = center_x + x * factor * scale
    y2d = center_y - y * factor * scale
    return x2d, y2d

def rotate_and_project():
    rotated_points = []
    for vertex in cube_vertices:
        x, y, z = vertex
        x, y, z = rotate_point(x, y, z)
        x2d, y2d = project_point(x, y, z)
        rotated_points.append((x2d, y2d))
    return rotated_points

def draw_scene():
    canvas.delete("all")
    
    for star in stars:
        x, y = star
        canvas.create_oval(x, y, x+2, y+2, fill="white", outline="")
    
    points = rotate_and_project()
    for edge in edges:
        i, j = edge
        x1, y1 = points[i]
        x2, y2 = points[j]
        canvas.create_line(x1, y1, x2, y2, fill="red", width=2)
    
    inputs_text = f"Inputs: X={slider_x.get():.2f}, Y={slider_y.get():.2f}, Z={slider_z.get():.2f}"
    canvas.create_text(10, canvas_height-10, anchor="sw", text=inputs_text, fill="white", font=("Helvetica", 10))
    
    aligned_flag = (abs(theta_x - target_angle) < tolerance and
                    abs(theta_y - target_angle) < tolerance and
                    abs(theta_z - target_angle) < tolerance)
    status_text = "Aligned: yes" if aligned_flag else "Aligned: no"
    canvas.create_text(canvas_width-10, canvas_height-10, anchor="se", text=status_text, fill="white", font=("Helvetica", 10))
    
    if aligned_flag:
        x, y, z = rotate_point(0, 0, 0.5)
        beam_start = project_point(x, y, z)
        dx = beam_start[0] - center_x
        dy = beam_start[1] - center_y
        beam_end = (beam_start[0] + 3 * dx, beam_start[1] + 3 * dy)
        canvas.create_line(beam_start[0], beam_start[1], beam_end[0], beam_end[1], fill="blue", width=3)

def update_simulation():
    global theta_x, theta_y, theta_z, omega_x, omega_y, omega_z
    global stabilizing, aligning, laser_timer

    if aligning:
        # PD control to drive each angle toward the 45° target
        k_p_align = 2.0
        k_d_align = 1.0
        torque_x = k_p_align * (target_angle - theta_x) - k_d_align * omega_x
        torque_y = k_p_align * (target_angle - theta_y) - k_d_align * omega_y
        torque_z = k_p_align * (target_angle - theta_z) - k_d_align * omega_z
    elif stabilizing:
        k_stab = 2.0
        torque_x = -k_stab * omega_x
        torque_y = -k_stab * omega_y
        torque_z = -k_stab * omega_z
    else:
        torque_x = slider_x.get()
        torque_y = slider_y.get()
        torque_z = slider_z.get()

    omega_x += torque_x * dt
    omega_y += torque_y * dt
    omega_z += torque_z * dt

    theta_x += omega_x * dt
    theta_y += omega_y * dt
    theta_z += omega_z * dt

    if stabilizing and abs(omega_x) < 0.01 and abs(omega_y) < 0.01 and abs(omega_z) < 0.01:
        omega_x = omega_y = omega_z = 0
        stabilizing = False

    draw_scene()
    root.after(int(dt * 1000), update_simulation)

def reset_sliders():
    slider_x.set(0)
    slider_y.set(0)
    slider_z.set(0)

def stabilize_command():
    global stabilizing, aligning
    stabilizing = True
    aligning = False

def align_command():
    global aligning, stabilizing
    aligning = True
    stabilizing = False

root = tk.Tk()
root.title("1U CubeSat Simulation")

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="black")
canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

control_frame = tk.Frame(root)
control_frame.pack(side=tk.BOTTOM, fill=tk.X)

slider_x = tk.Scale(control_frame, from_=-1, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                    label="Reaction Wheel X", length=250)
slider_x.pack(side=tk.LEFT, padx=5, pady=5)
slider_y = tk.Scale(control_frame, from_=-1, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                    label="Reaction Wheel Y", length=250)
slider_y.pack(side=tk.LEFT, padx=5, pady=5)
slider_z = tk.Scale(control_frame, from_=-1, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                    label="Reaction Wheel Z", length=250)
slider_z.pack(side=tk.LEFT, padx=5, pady=5)

button_frame = tk.Frame(control_frame)
button_frame.pack(side=tk.LEFT, padx=10)

reset_button = tk.Button(button_frame, text="Reset", command=reset_sliders)
reset_button.pack(pady=2)

stabilize_button = tk.Button(button_frame, text="Stabilize", command=stabilize_command)
stabilize_button.pack(pady=2)

align_button = tk.Button(button_frame, text="Align", command=align_command)
align_button.pack(pady=2)

slider_x.set(0)
slider_y.set(0)
slider_z.set(0)

update_simulation()
root.mainloop()
