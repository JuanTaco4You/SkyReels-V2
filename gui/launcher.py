import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

MODEL_OPTIONS = [
    "Skywork/SkyReels-V2-T2V-14B-540P",
    "Skywork/SkyReels-V2-T2V-14B-720P",
    "Skywork/SkyReels-V2-I2V-14B-540P",
    "Skywork/SkyReels-V2-I2V-14B-720P",
    "Skywork/SkyReels-V2-DF-14B-720P",
]

SCRIPTS = {
    'Standard Generation': 'generate_video.py',
    'Diffusion Forcing': 'generate_video_df.py',
}


def run_command(cmd, text_widget):
    process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in process.stdout:
        text_widget.insert(tk.END, line)
        text_widget.see(tk.END)
    process.wait()
    text_widget.insert(tk.END, f"\nFinished with exit code {process.returncode}\n")


def threaded(cmd, text_widget):
    thread = threading.Thread(target=run_command, args=(cmd, text_widget))
    thread.start()


def install_deps(output):
    cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
    threaded(cmd, output)


def run_generation(script_var, model_var, prompt_widget, image_var, res_var,
                   frames_var, guidance_var, outdir_var, output):
    script_name = SCRIPTS[script_var.get()]
    cmd = [sys.executable, os.path.join(PROJECT_ROOT, script_name)]
    if model_var.get():
        cmd.extend(['--model_id', model_var.get()])
    if res_var.get():
        cmd.extend(['--resolution', res_var.get()])
    if frames_var.get():
        cmd.extend(['--num_frames', frames_var.get()])
    if guidance_var.get():
        cmd.extend(['--guidance_scale', guidance_var.get()])
    if outdir_var.get():
        cmd.extend(['--outdir', outdir_var.get()])
    if image_var.get():
        cmd.extend(['--image', image_var.get()])
    prompt_text = prompt_widget.get("1.0", "end").strip()
    if prompt_text:
        cmd.extend(['--prompt', prompt_text])

    output.delete(1.0, tk.END)
    threaded(cmd, output)


def browse_image(var):
    path = filedialog.askopenfilename()
    if path:
        var.set(path)


def browse_output(var):
    path = filedialog.askdirectory()
    if path:
        var.set(path)


def apply_theme(root, is_dark):
    if is_dark:
        bg_color = '#333333'  # Dark gray
        fg_color = '#ffffff'  # White
        root.configure(background=bg_color)
        # Add any dark mode style changes here
    else:
        bg_color = '#f0f0f0'  # Light gray
        fg_color = '#000000'  # Black
        root.configure(background=bg_color)
        # Add any light mode style changes here
        style.theme_use('default')
        root.configure(background='SystemButtonFace')
        style.configure('.', background='SystemButtonFace', foreground='SystemButtonText')
        style.configure('TEntry', fieldbackground='white')
        style.configure('TCombobox', fieldbackground='white')


def main():
    root = tk.Tk()
    root.title('SkyReels Launcher')

    script_var = tk.StringVar(value='Standard Generation')
    model_var = tk.StringVar(value=MODEL_OPTIONS[0])
    image_var = tk.StringVar()
    res_var = tk.StringVar(value='540P')
    frames_var = tk.StringVar(value='97')
    guidance_var = tk.StringVar(value='6.0')
    outdir_var = tk.StringVar(value='video_out')
    dark_var = tk.BooleanVar(value=False)

    ttk.Label(root, text='Script').grid(row=0, column=0, sticky='w')
    ttk.Combobox(root, textvariable=script_var, values=list(SCRIPTS.keys()), width=30).grid(row=0, column=1, sticky='ew')
    ttk.Checkbutton(root, text='Dark Mode', variable=dark_var, command=lambda: apply_theme(root, dark_var.get())).grid(row=0, column=2, sticky='w')

    ttk.Label(root, text='Model').grid(row=1, column=0, sticky='w')
    ttk.Combobox(root, textvariable=model_var, values=MODEL_OPTIONS, width=60).grid(row=1, column=1, sticky='ew')

    ttk.Label(root, text='Prompt').grid(row=2, column=0, sticky='nw')
    prompt_widget = scrolledtext.ScrolledText(root, width=60, height=4)
    prompt_widget.grid(row=2, column=1, sticky='ew')

    ttk.Label(root, text='Image').grid(row=3, column=0, sticky='w')
    img_entry = tk.Entry(root, textvariable=image_var, width=50)
    img_entry.grid(row=3, column=1, sticky='w')
    ttk.Button(root, text='Browse', command=lambda: browse_image(image_var)).grid(row=3, column=2, sticky='w')

    ttk.Label(root, text='Resolution').grid(row=4, column=0, sticky='w')
    ttk.Combobox(root, textvariable=res_var, values=['540P', '720P'], width=10).grid(row=4, column=1, sticky='w')

    ttk.Label(root, text='Frames').grid(row=5, column=0, sticky='w')
    tk.Entry(root, textvariable=frames_var, width=10).grid(row=5, column=1, sticky='w')

    ttk.Label(root, text='Guidance').grid(row=6, column=0, sticky='w')
    tk.Entry(root, textvariable=guidance_var, width=10).grid(row=6, column=1, sticky='w')

    ttk.Label(root, text='Output Dir').grid(row=7, column=0, sticky='w')
    out_entry = tk.Entry(root, textvariable=outdir_var, width=50)
    out_entry.grid(row=7, column=1, sticky='w')
    ttk.Button(root, text='Browse', command=lambda: browse_output(outdir_var)).grid(row=7, column=2, sticky='w')

    output = scrolledtext.ScrolledText(root, width=80, height=20)
    output.grid(row=9, column=0, columnspan=3, pady=5)

    ttk.Button(root, text='Install Dependencies', command=lambda: install_deps(output)).grid(row=8, column=0, pady=5)
    ttk.Button(root, text='Run', command=lambda: run_generation(script_var, model_var, prompt_widget, image_var, res_var, frames_var, guidance_var, outdir_var, output)).grid(row=8, column=1, pady=5)
    ttk.Button(root, text='Quit', command=root.destroy).grid(row=8, column=2, pady=5)

    apply_theme(root, dark_var.get())
    root.mainloop()


if __name__ == '__main__':
    main()
