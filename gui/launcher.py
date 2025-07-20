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
    shift_var,
    fps_var,
    seed_var,
    offload_var,
    use_usp_var,
    teacache_var,
    teacache_thresh_var,
    use_ret_steps_var,
    video_path_var,
    end_image_var,
    ar_step_var,
    base_frames_var,
    overlap_history_var,
    addnoise_var,
    causal_block_size_var,
    output,
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
    if shift_var.get():
        cmd.extend(["--shift", shift_var.get()])
    if fps_var.get():
        cmd.extend(["--fps", fps_var.get()])
    if seed_var.get():
        cmd.extend(["--seed", seed_var.get()])
    if offload_var.get():
        cmd.append("--offload")
    if use_usp_var.get():
        cmd.append("--use_usp")
    if teacache_var.get():
        cmd.append("--teacache")
    if teacache_thresh_var.get():
        cmd.extend(["--teacache_thresh", teacache_thresh_var.get()])
    if use_ret_steps_var.get():
        cmd.append("--use_ret_steps")
    if video_path_var.get():
        cmd.extend(["--video_path", video_path_var.get()])
    if end_image_var.get():
        cmd.extend(["--end_image", end_image_var.get()])
    if ar_step_var.get():
        cmd.extend(["--ar_step", ar_step_var.get()])
    if base_frames_var.get():
        cmd.extend(["--base_num_frames", base_frames_var.get()])
    if overlap_history_var.get():
        cmd.extend(["--overlap_history", overlap_history_var.get()])
    if addnoise_var.get():
        cmd.extend(["--addnoise_condition", addnoise_var.get()])
    if causal_block_size_var.get():
        cmd.extend(["--causal_block_size", causal_block_size_var.get()])
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
    script_path = os.path.join(PROJECT_ROOT, "skyreels_v2_infer", "pipelines", "prompt_enhancer.py")
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
    shift_var = tk.StringVar(value="8.0")
    fps_var = tk.StringVar(value="24")
    seed_var = tk.StringVar()
    offload_var = tk.BooleanVar()
    use_usp_var = tk.BooleanVar()
    teacache_var = tk.BooleanVar()
    teacache_thresh_var = tk.StringVar(value="0.2")
    use_ret_steps_var = tk.BooleanVar()
    video_path_var = tk.StringVar()
    end_image_var = tk.StringVar()
    ar_step_var = tk.StringVar(value="0")
    base_frames_var = tk.StringVar(value="97")
    overlap_history_var = tk.StringVar()
    addnoise_var = tk.StringVar(value="0")
    causal_block_size_var = tk.StringVar(value="1")

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
    ttk.Combobox(enhancer_frame, textvariable=prompt_enhancer_model_size_var, values=["small", "large"], width=10).pack(
        side="left"
    )

    extra_frame = ttk.LabelFrame(root, text="Common Options")
    extra_frame.grid(row=9, column=0, columnspan=3, sticky="ew", pady=5)

    ttk.Label(extra_frame, text="Shift").grid(row=0, column=0, sticky="w")
    tk.Entry(extra_frame, textvariable=shift_var, width=10).grid(row=0, column=1, sticky="w")

    ttk.Label(extra_frame, text="FPS").grid(row=0, column=2, sticky="w")
    tk.Entry(extra_frame, textvariable=fps_var, width=10).grid(row=0, column=3, sticky="w")

    ttk.Label(extra_frame, text="Seed").grid(row=1, column=0, sticky="w")
    tk.Entry(extra_frame, textvariable=seed_var, width=10).grid(row=1, column=1, sticky="w")

    ttk.Checkbutton(extra_frame, text="Offload", variable=offload_var).grid(row=1, column=2, sticky="w")
    ttk.Checkbutton(extra_frame, text="Use USP", variable=use_usp_var).grid(row=1, column=3, sticky="w")

    ttk.Checkbutton(extra_frame, text="Teacache", variable=teacache_var).grid(row=2, column=0, sticky="w")
    ttk.Label(extra_frame, text="Thresh").grid(row=2, column=1, sticky="w")
    tk.Entry(extra_frame, textvariable=teacache_thresh_var, width=6).grid(row=2, column=2, sticky="w")
    ttk.Checkbutton(extra_frame, text="Use Ret Steps", variable=use_ret_steps_var).grid(row=2, column=3, sticky="w")

    df_frame = ttk.LabelFrame(root, text="Diffusion Forcing")
    df_frame.grid(row=10, column=0, columnspan=3, sticky="ew", pady=5)

    ttk.Label(df_frame, text="Video Path").grid(row=0, column=0, sticky="w")
    video_entry = tk.Entry(df_frame, textvariable=video_path_var, width=40)
    video_entry.grid(row=0, column=1, sticky="w")
    ttk.Button(df_frame, text="Browse", command=lambda: browse_image(video_path_var)).grid(row=0, column=2, sticky="w")

    ttk.Label(df_frame, text="End Image").grid(row=1, column=0, sticky="w")
    end_entry = tk.Entry(df_frame, textvariable=end_image_var, width=40)
    end_entry.grid(row=1, column=1, sticky="w")
    ttk.Button(df_frame, text="Browse", command=lambda: browse_image(end_image_var)).grid(row=1, column=2, sticky="w")

    ttk.Label(df_frame, text="AR Step").grid(row=2, column=0, sticky="w")
    ar_step_entry = tk.Entry(df_frame, textvariable=ar_step_var, width=6)
    ar_step_entry.grid(row=2, column=1, sticky="w")
    ttk.Label(df_frame, text="Base Frames").grid(row=2, column=2, sticky="w")
    base_frames_entry = tk.Entry(df_frame, textvariable=base_frames_var, width=6)
    base_frames_entry.grid(row=2, column=3, sticky="w")

    ttk.Label(df_frame, text="Overlap Hist").grid(row=3, column=0, sticky="w")
    overlap_entry = tk.Entry(df_frame, textvariable=overlap_history_var, width=6)
    overlap_entry.grid(row=3, column=1, sticky="w")
    ttk.Label(df_frame, text="Addnoise").grid(row=3, column=2, sticky="w")
    addnoise_entry = tk.Entry(df_frame, textvariable=addnoise_var, width=6)
    addnoise_entry.grid(row=3, column=3, sticky="w")

    ttk.Label(df_frame, text="Causal Block").grid(row=4, column=0, sticky="w")
    causal_entry = tk.Entry(df_frame, textvariable=causal_block_size_var, width=6)
    causal_entry.grid(row=4, column=1, sticky="w")

    df_widgets = [
        video_entry,
        end_entry,
        ar_step_entry,
        base_frames_entry,
        overlap_entry,
        addnoise_entry,
        causal_entry,
    ]

    def update_fields(*_):
        state = "normal" if script_var.get() == "Diffusion Forcing" else "disabled"
        for w in df_widgets:
            w.configure(state=state)

    script_var.trace_add("write", update_fields)
    update_fields()

    output = scrolledtext.ScrolledText(root, width=80, height=20)
    output.grid(row=12, column=0, columnspan=4, pady=5)

    run_button = ttk.Button(
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
            shift_var,
            fps_var,
            seed_var,
            offload_var,
            use_usp_var,
            teacache_var,
            teacache_thresh_var,
            use_ret_steps_var,
            video_path_var,
            end_image_var,
            ar_step_var,
            base_frames_var,
            overlap_history_var,
            addnoise_var,
            causal_block_size_var,
            output,
        ),
        state="disabled",
    )
    run_button.grid(row=11, column=1, pady=5)

    enhancer_button = ttk.Button(
        root,
        text="Prompt Enhancer",
        command=lambda: open_prompt_enhancer(prompt_widget),
        state="disabled",
    )
    enhancer_button.grid(row=11, column=2, pady=5)

    ttk.Button(
        root,
        text="Install Dependencies",
        command=lambda: install_deps(output, run_button, enhancer_button),
    ).grid(row=11, column=0, pady=5)

    ttk.Button(root, text="Quit", command=root.destroy).grid(row=11, column=3, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
