import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk


def apply_dark_mode(root, widgets, enabled):
    """Apply a basic dark or light theme to the given widgets."""
    style = ttk.Style()
    if enabled:
        bg = "#2b2b2b"
        fg = "#ffffff"
        style.theme_use("clam")
        style.configure(".", background=bg, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TButton", background="#444444", foreground=fg)
        style.configure("TCombobox", fieldbackground="#3c3c3c", background="#444444", foreground=fg)
        root.configure(bg=bg)
        for w in widgets:
            w.configure(bg="#3c3c3c", fg=fg, insertbackground=fg)
    else:
        style.theme_use("default")
        style.configure(".", background=root.default_bg, foreground="black")
        style.configure("TLabel", background=root.default_bg, foreground="black")
        style.configure("TButton", background=root.default_bg, foreground="black")
        style.configure("TCombobox", fieldbackground="white", background=root.default_bg, foreground="black")
        root.configure(bg=root.default_bg)
        for w in widgets:
            w.configure(bg="white", fg="black", insertbackground="black")


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

MODEL_OPTIONS = [
    "Skywork/SkyReels-V2-T2V-14B-540P",
    "Skywork/SkyReels-V2-T2V-14B-720P",
    "Skywork/SkyReels-V2-I2V-14B-540P",
    "Skywork/SkyReels-V2-I2V-14B-720P",
    "Skywork/SkyReels-V2-DF-14B-720P",
]

SCRIPTS = {
    "Standard Generation": "generate_video.py",
    "Diffusion Forcing": "generate_video_df.py",
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
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    threaded(cmd, output)


def run_generation(
    script_var, model_var, prompt_widget, image_var, res_var, frames_var, guidance_var, outdir_var, output
):
    script_name = SCRIPTS[script_var.get()]
    cmd = [sys.executable, os.path.join(PROJECT_ROOT, script_name)]
    if model_var.get():
        cmd.extend(["--model_id", model_var.get()])
    if res_var.get():
        cmd.extend(["--resolution", res_var.get()])
    if frames_var.get():
        cmd.extend(["--num_frames", frames_var.get()])
    if guidance_var.get():
        cmd.extend(["--guidance_scale", guidance_var.get()])
    if outdir_var.get():
        cmd.extend(["--outdir", outdir_var.get()])
    if image_var.get():
        cmd.extend(["--image", image_var.get()])
    prompt_text = prompt_widget.get("1.0", "end").strip()
    if prompt_text:
        cmd.extend(["--prompt", prompt_text])

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


def main():
    root = tk.Tk()
    root.title("SkyReels Launcher")
    root.default_bg = root.cget("bg")

    script_var = tk.StringVar(value="Standard Generation")
    model_var = tk.StringVar(value=MODEL_OPTIONS[0])
    image_var = tk.StringVar()
    res_var = tk.StringVar(value="540P")
    frames_var = tk.StringVar(value="97")
    guidance_var = tk.StringVar(value="6.0")
    outdir_var = tk.StringVar(value="video_out")
    dark_mode_var = tk.BooleanVar(value=False)

    ttk.Label(root, text="Script").grid(row=0, column=0, sticky="w")
    ttk.Combobox(root, textvariable=script_var, values=list(SCRIPTS.keys()), width=30).grid(
        row=0, column=1, sticky="ew"
    )

    ttk.Label(root, text="Model").grid(row=1, column=0, sticky="w")
    ttk.Combobox(root, textvariable=model_var, values=MODEL_OPTIONS, width=60).grid(row=1, column=1, sticky="ew")

    ttk.Label(root, text="Prompt").grid(row=2, column=0, sticky="nw")
    prompt_widget = scrolledtext.ScrolledText(root, width=60, height=4)
    prompt_widget.grid(row=2, column=1, sticky="ew")

    ttk.Label(root, text="Image").grid(row=3, column=0, sticky="w")
    img_entry = tk.Entry(root, textvariable=image_var, width=50)
    img_entry.grid(row=3, column=1, sticky="w")
    ttk.Button(root, text="Browse", command=lambda: browse_image(image_var)).grid(row=3, column=2, sticky="w")

    ttk.Label(root, text="Resolution").grid(row=4, column=0, sticky="w")
    ttk.Combobox(root, textvariable=res_var, values=["540P", "720P"], width=10).grid(row=4, column=1, sticky="w")

    ttk.Label(root, text="Frames").grid(row=5, column=0, sticky="w")
    frames_entry = tk.Entry(root, textvariable=frames_var, width=10)
    frames_entry.grid(row=5, column=1, sticky="w")

    ttk.Label(root, text="Guidance").grid(row=6, column=0, sticky="w")
    guidance_entry = tk.Entry(root, textvariable=guidance_var, width=10)
    guidance_entry.grid(row=6, column=1, sticky="w")

    ttk.Label(root, text="Output Dir").grid(row=7, column=0, sticky="w")
    out_entry = tk.Entry(root, textvariable=outdir_var, width=50)
    out_entry.grid(row=7, column=1, sticky="w")
    ttk.Button(root, text="Browse", command=lambda: browse_output(outdir_var)).grid(row=7, column=2, sticky="w")

    output = scrolledtext.ScrolledText(root, width=80, height=20)
    output.grid(row=9, column=0, columnspan=4, pady=5)

    ttk.Button(root, text="Install Dependencies", command=lambda: install_deps(output)).grid(row=8, column=0, pady=5)
    ttk.Button(
        root,
        text="Run",
        command=lambda: run_generation(
            script_var, model_var, prompt_widget, image_var, res_var, frames_var, guidance_var, outdir_var, output
        ),
    ).grid(row=8, column=1, pady=5)
    ttk.Button(root, text="Quit", command=root.destroy).grid(row=8, column=2, pady=5)
    ttk.Checkbutton(
        root,
        text="Dark Mode",
        variable=dark_mode_var,
        command=lambda: apply_dark_mode(
            root, [img_entry, frames_entry, guidance_entry, out_entry, prompt_widget, output], dark_mode_var.get()
        ),
    ).grid(row=8, column=3, pady=5)

    apply_dark_mode(
        root, [img_entry, frames_entry, guidance_entry, out_entry, prompt_widget, output], dark_mode_var.get()
    )

    root.mainloop()


if __name__ == "__main__":
    main()
