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


def check_deps():
    try:
        import torch
        import transformers
        return True
    except ImportError:
        return False

def install_deps(output, run_button, enhancer_button):
    output.insert(tk.END, "Installing dependencies...\n")
    output.see(tk.END)

    def install_and_update_ui():
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in process.stdout:
            output.insert(tk.END, line)
            output.see(tk.END)
        process.wait()
        if process.returncode == 0:
            output.insert(tk.END, "\nDependencies installed successfully.\n")
            run_button.config(state="normal")
            enhancer_button.config(state="normal")
        else:
            output.insert(tk.END, f"\nFailed to install dependencies. Exit code: {process.returncode}\n")

    thread = threading.Thread(target=install_and_update_ui)
    thread.start()


def run_generation(
    script_var, model_var, prompt_widget, image_var, res_var, frames_var, guidance_var, outdir_var, enhancer_var, prompt_enhancer_model_size_var, output
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
        cmd.extend(["--prompt_enhancer_model_size", prompt_enhancer_model_size_var.get()])

    output.delete(1.0, tk.END)
    threaded(cmd, output)


def run_prompt_enhancer(prompt_widget, output_widget, model_size_var, status_var):
    """Run the standalone prompt enhancer script with the given prompt."""
    prompt_text = prompt_widget.get("1.0", "end").strip()
    if not prompt_text:
        output_widget.insert(tk.END, "Prompt is empty\n")
        output_widget.see(tk.END)
        return

    model_size = model_size_var.get()
    script_path = os.path.join(
        PROJECT_ROOT, "skyreels_v2_infer", "pipelines", "prompt_enhancer.py"
    )
    cmd = [sys.executable, script_path, "--prompt", prompt_text, "--model_size", model_size]
    output_widget.delete(1.0, tk.END)

    def update_status(message):
        status_var.set(message)
        output_widget.insert(tk.END, message + "\n")
        output_widget.see(tk.END)

    def run_and_update():
        update_status(f"Loading {model_size} model...")
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in process.stdout:
            output_widget.insert(tk.END, line)
            output_widget.see(tk.END)
        process.wait()
        update_status(f"Finished with exit code {process.returncode}")

    thread = threading.Thread(target=run_and_update)
    thread.start()


def open_prompt_enhancer(prompt_widget):
    """Open a simple window to run the prompt enhancer separately."""
    win = tk.Toplevel()
    win.title("Prompt Enhancer")

    model_size_var = tk.StringVar(value="small")
    status_var = tk.StringVar(value="Idle")

    main_frame = ttk.Frame(win)
    main_frame.pack(padx=10, pady=10, fill="both", expand=True)

    top_frame = ttk.Frame(main_frame)
    top_frame.pack(fill="x", expand=True)

    ttk.Label(top_frame, text="Prompt:").pack(side="left", padx=(0, 5))
    input_box = scrolledtext.ScrolledText(top_frame, width=60, height=4)
    input_box.pack(side="left", fill="x", expand=True)
    input_box.insert(tk.END, prompt_widget.get("1.0", "end").strip())

    ttk.Label(top_frame, text="Model:").pack(side="left", padx=(10, 5))
    model_menu = ttk.Combobox(top_frame, textvariable=model_size_var, values=["small", "large"], width=10)
    model_menu.pack(side="left")

    output_box = scrolledtext.ScrolledText(main_frame, width=80, height=10)
    output_box.pack(pady=5, fill="both", expand=True)

    status_bar = ttk.Label(main_frame, textvariable=status_var, relief=tk.SUNKEN, anchor="w")
    status_bar.pack(side="bottom", fill="x")

    ttk.Button(
        main_frame,
        text="Enhance Prompt",
        command=lambda: run_prompt_enhancer(input_box, output_box, model_size_var, status_var),
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

    enhancer_frame = ttk.Frame(root)
    enhancer_frame.grid(row=8, column=0, columnspan=2, sticky="w")
    ttk.Checkbutton(enhancer_frame, text="Use Prompt Enhancer", variable=enhancer_var).pack(side="left")

    prompt_enhancer_model_size_var = tk.StringVar(value="small")
    ttk.Label(enhancer_frame, text="Model Size:").pack(side="left", padx=(10, 0))
    ttk.Combobox(enhancer_frame, textvariable=prompt_enhancer_model_size_var, values=["small", "large"], width=10).pack(side="left")

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
            prompt_enhancer_model_size_var,
            output,
        ),
    ).grid(row=9, column=1, pady=5)
    ttk.Button(root, text="Prompt Enhancer", command=lambda: open_prompt_enhancer(prompt_widget)).grid(row=9, column=2, pady=5)
    ttk.Button(root, text="Quit", command=root.destroy).grid(row=9, column=3, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
