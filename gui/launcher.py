import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk

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
    script_var, model_var, prompt_widget, image_var, res_var, frames_var, guidance_var, outdir_var, enhancer_var, output
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
    if enhancer_var.get():
        cmd.append("--prompt_enhancer")

    output.delete(1.0, tk.END)
    threaded(cmd, output)


def run_prompt_enhancer(prompt_widget, output_widget):
    """Run the standalone prompt enhancer script with the given prompt."""
    prompt_text = prompt_widget.get("1.0", "end").strip()
    if not prompt_text:
        output_widget.insert(tk.END, "Prompt is empty\n")
        output_widget.see(tk.END)
        return

    script_path = os.path.join(
        PROJECT_ROOT, "skyreels_v2_infer", "pipelines", "prompt_enhancer.py"
    )
    cmd = [sys.executable, script_path, "--prompt", prompt_text]
    output_widget.delete(1.0, tk.END)
    threaded(cmd, output_widget)


def open_prompt_enhancer(prompt_widget):
    """Open a simple window to run the prompt enhancer separately."""
    win = tk.Toplevel()
    win.title("Prompt Enhancer")

    input_box = scrolledtext.ScrolledText(win, width=60, height=4)
    input_box.pack(padx=5, pady=5, fill="both")
    input_box.insert(tk.END, prompt_widget.get("1.0", "end").strip())

    output_box = scrolledtext.ScrolledText(win, width=80, height=10)
    output_box.pack(padx=5, pady=5, fill="both")

    ttk.Button(
        win,
        text="Start",
        command=lambda: run_prompt_enhancer(input_box, output_box),
    ).pack(pady=5)



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

    script_var = tk.StringVar(value="Standard Generation")
    model_var = tk.StringVar(value=MODEL_OPTIONS[0])
    image_var = tk.StringVar()
    res_var = tk.StringVar(value="540P")
    frames_var = tk.StringVar(value="97")
    guidance_var = tk.StringVar(value="6.0")
    outdir_var = tk.StringVar(value="video_out")
    enhancer_var = tk.BooleanVar()

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
    tk.Entry(root, textvariable=frames_var, width=10).grid(row=5, column=1, sticky="w")

    ttk.Label(root, text="Guidance").grid(row=6, column=0, sticky="w")
    tk.Entry(root, textvariable=guidance_var, width=10).grid(row=6, column=1, sticky="w")

    ttk.Label(root, text="Output Dir").grid(row=7, column=0, sticky="w")
    out_entry = tk.Entry(root, textvariable=outdir_var, width=50)
    out_entry.grid(row=7, column=1, sticky="w")
    ttk.Button(root, text="Browse", command=lambda: browse_output(outdir_var)).grid(row=7, column=2, sticky="w")

    ttk.Checkbutton(root, text="Use Prompt Enhancer", variable=enhancer_var).grid(
        row=8, column=0, columnspan=2, sticky="w"
    )
    output = scrolledtext.ScrolledText(root, width=80, height=20)
    output.grid(row=10, column=0, columnspan=4, pady=5)

    ttk.Button(root, text="Install Dependencies", command=lambda: install_deps(output)).grid(row=9, column=0, pady=5)
    ttk.Button(
        root,
        text="Run",
        command=lambda: run_generation(
            script_var,
            model_var,
            prompt_widget,
            image_var,
            res_var,
            frames_var,
            guidance_var,
            outdir_var,
            enhancer_var,
            output,
        ),
    ).grid(row=9, column=1, pady=5)
    ttk.Button(root, text="Prompt Enhancer", command=lambda: open_prompt_enhancer(prompt_widget)).grid(row=9, column=2, pady=5)
    ttk.Button(root, text="Quit", command=root.destroy).grid(row=9, column=3, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
