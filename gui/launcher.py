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
    "Skywork/SkyReels-V2-DF-1.3B-540P",
    "Skywork/SkyReels-V2-I2V-1.3B-540P",
    "Skywork/SkyReels-V2-T2V-1.3B-540P",
    "Skywork/SkyReels-V2-T2V-14B-540P",
    "Skywork/SkyReels-V2-T2V-14B-720P",
    "Skywork/SkyReels-V2-I2V-14B-540P",
    "Skywork/SkyReels-V2-I2V-14B-720P",
    "Skywork/SkyReels-V2-DF-14B-720P",
    "Skywork/SkyReels-V2-DF-5B-540P",
    "Skywork/SkyReels-V2-DF-5B-720P",
    "Skywork/SkyReels-V2-T2V-5B-540P",
    "Skywork/SkyReels-V2-T2V-5B-720P",
    "Skywork/SkyReels-V2-I2V-5B-540P",
    "Skywork/SkyReels-V2-I2V-5B-720P",
    "Skywork/SkyReels-V2-CD-5B-540P",
    "Skywork/SkyReels-V2-CD-5B-720P",
    "Skywork/SkyReels-V2-CD-14B-720P",
]

SCRIPTS = {
    "Standard Generation": "generate_video.py",
    "Diffusion Forcing": "generate_video_df.py",
}


def run_command(app, cmd, text_widget):
    app.process = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for line in app.process.stdout:
        text_widget.insert(tk.END, line)
        text_widget.see(tk.END)
    app.process.wait()
    text_widget.insert(tk.END, f"\nFinished with exit code {app.process.returncode}\n")
    app.cancel_button.config(state="disabled")
    app.run_button.config(state="normal")


def threaded(app, cmd, text_widget):
    thread = threading.Thread(target=run_command, args=(app, cmd, text_widget))
    thread.start()


def install_deps(output, run_button, enhancer_button, caption_button):
    output.insert(tk.END, "Installing dependencies...\n")
    output.see(tk.END)

    def install_and_update_ui():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        except subprocess.CalledProcessError:
            output.insert(tk.END, "\nError: pip is not installed. Please install pip and try again.\n")
            return

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
            caption_button.config(state="normal")
        else:
            output.insert(
                tk.END,
                f"\nFailed to install dependencies. Exit code: {process.returncode}\n"
                "Please check the console for more information.\n",
            )

    thread = threading.Thread(target=install_and_update_ui)
    thread.start()


def run_generation(
    app,
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

    if script_name == "generate_video_df.py":
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
    threaded(app, cmd, output)


def run_prompt_enhancer(prompt_widget, output_widget, model_size_var, status_var, max_length_var):
    """Run the standalone prompt enhancer script with the given prompt."""
    prompt_text = prompt_widget.get("1.0", "end").strip()
    if not prompt_text:
        output_widget.insert(tk.END, "Prompt is empty\n")
        output_widget.see(tk.END)
        return

    model_size = model_size_var.get()
    script_path = os.path.join(PROJECT_ROOT, "skyreels_v2_infer", "pipelines", "prompt_enhancer.py")
    cmd = [sys.executable, script_path, "--prompt", prompt_text, "--model_size", model_size]
    if max_length_var.get():
        cmd.extend(["--max_length", max_length_var.get()])
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
    max_length_var = tk.StringVar(value="256")

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

    ttk.Label(top_frame, text="Max Length:").pack(side="left", padx=(10, 5))
    max_length_entry = tk.Entry(top_frame, textvariable=max_length_var, width=10)
    max_length_entry.pack(side="left")

    output_box = scrolledtext.ScrolledText(main_frame, width=80, height=10)
    output_box.pack(pady=5, fill="both", expand=True)

    status_bar = ttk.Label(main_frame, textvariable=status_var, relief=tk.SUNKEN, anchor="w")
    status_bar.pack(side="bottom", fill="x")

    ttk.Button(
        main_frame,
        text="Enhance Prompt",
        command=lambda: run_prompt_enhancer(input_box, output_box, model_size_var, status_var, max_length_var),
    ).pack(pady=5)


def open_captioner():
    """Open a window to run SkyCaptioner scripts."""
    win = tk.Toplevel()
    win.title("SkyCaptioner")

    notebook = ttk.Notebook(win)
    notebook.pack(padx=10, pady=10, fill="both", expand=True)

    # Structured Caption Tab
    struct_tab = ttk.Frame(notebook)
    notebook.add(struct_tab, text="Structured Caption")

    sc_model_var = tk.StringVar()
    sc_video_var = tk.StringVar()
    sc_csv_var = tk.StringVar()
    sc_tp_var = tk.StringVar(value="2")

    ttk.Label(struct_tab, text="Model Path").grid(row=0, column=0, sticky="w")
    sc_model_entry = tk.Entry(struct_tab, textvariable=sc_model_var, width=50)
    sc_model_entry.grid(row=0, column=1, sticky="w")
    ttk.Button(struct_tab, text="Browse", command=lambda: browse_image(sc_model_var)).grid(row=0, column=2, sticky="w")

    ttk.Label(struct_tab, text="Video File").grid(row=1, column=0, sticky="w")
    sc_video_entry = tk.Entry(struct_tab, textvariable=sc_video_var, width=50)
    sc_video_entry.grid(row=1, column=1, sticky="w")
    ttk.Button(struct_tab, text="Browse", command=lambda: browse_image(sc_video_var)).grid(row=1, column=2, sticky="w")

    ttk.Label(struct_tab, text="CSV File").grid(row=2, column=0, sticky="w")
    sc_csv_entry = tk.Entry(struct_tab, textvariable=sc_csv_var, width=50)
    sc_csv_entry.grid(row=2, column=1, sticky="w")
    ttk.Button(struct_tab, text="Browse", command=lambda: browse_image(sc_csv_var)).grid(row=2, column=2, sticky="w")

    ttk.Label(struct_tab, text="Tensor Parallel").grid(row=3, column=0, sticky="w")
    tk.Entry(struct_tab, textvariable=sc_tp_var, width=6).grid(row=3, column=1, sticky="w")

    sc_output = scrolledtext.ScrolledText(struct_tab, width=80, height=15)
    sc_output.grid(row=4, column=0, columnspan=3, pady=5)

    def run_struct():
        sc_output.delete(1.0, tk.END)
        if sc_csv_var.get():
            out_csv = os.path.splitext(sc_csv_var.get())[0] + "_struct_caption.csv"
            script_path = os.path.join(PROJECT_ROOT, "skycaptioner_v1", "scripts", "vllm_struct_caption.py")
            cmd = [sys.executable, script_path, "--input_csv", sc_csv_var.get(), "--out_csv", out_csv, "--model_path", sc_model_var.get(), "--tp", sc_tp_var.get()]
            threaded(cmd, sc_output)
        elif sc_video_var.get():
            from skycaptioner_v1.scripts.gradio_struct_caption import StructCaptioner
            try:
                cap = StructCaptioner(sc_model_var.get(), int(sc_tp_var.get()))
                result = cap(sc_video_var.get())
                sc_output.insert(tk.END, result)
            except Exception as e:
                sc_output.insert(tk.END, str(e))
        else:
            sc_output.insert(tk.END, "Please provide a video or CSV file\n")

    ttk.Button(struct_tab, text="Run", command=run_struct).grid(row=5, column=1, pady=5)

    # Fusion Caption Tab
    fusion_tab = ttk.Frame(notebook)
    notebook.add(fusion_tab, text="Caption Fusion")

    fc_model_var = tk.StringVar()
    fc_csv_var = tk.StringVar()
    fc_tp_var = tk.StringVar(value="2")
    fc_task_var = tk.StringVar(value="t2v")

    ttk.Label(fusion_tab, text="Model Path").grid(row=0, column=0, sticky="w")
    fc_model_entry = tk.Entry(fusion_tab, textvariable=fc_model_var, width=50)
    fc_model_entry.grid(row=0, column=1, sticky="w")
    ttk.Button(fusion_tab, text="Browse", command=lambda: browse_image(fc_model_var)).grid(row=0, column=2, sticky="w")

    ttk.Label(fusion_tab, text="Input CSV").grid(row=1, column=0, sticky="w")
    fc_csv_entry = tk.Entry(fusion_tab, textvariable=fc_csv_var, width=50)
    fc_csv_entry.grid(row=1, column=1, sticky="w")
    ttk.Button(fusion_tab, text="Browse", command=lambda: browse_image(fc_csv_var)).grid(row=1, column=2, sticky="w")

    ttk.Label(fusion_tab, text="Task").grid(row=2, column=0, sticky="w")
    ttk.Combobox(fusion_tab, textvariable=fc_task_var, values=["t2v", "i2v"], width=10).grid(row=2, column=1, sticky="w")

    ttk.Label(fusion_tab, text="Tensor Parallel").grid(row=3, column=0, sticky="w")
    tk.Entry(fusion_tab, textvariable=fc_tp_var, width=6).grid(row=3, column=1, sticky="w")

    fc_struct_text = scrolledtext.ScrolledText(fusion_tab, width=80, height=10)
    fc_struct_text.grid(row=4, column=0, columnspan=3, pady=5)

    fc_output = scrolledtext.ScrolledText(fusion_tab, width=80, height=10)
    fc_output.grid(row=5, column=0, columnspan=3, pady=5)

    def run_fusion():
        fc_output.delete(1.0, tk.END)
        if fc_csv_var.get():
            out_csv = os.path.splitext(fc_csv_var.get())[0] + "_fusion_caption.csv"
            script_path = os.path.join(PROJECT_ROOT, "skycaptioner_v1", "scripts", "vllm_fusion_caption.py")
            cmd = [sys.executable, script_path, "--input_csv", fc_csv_var.get(), "--out_csv", out_csv, "--model_path", fc_model_var.get(), "--tp", fc_tp_var.get(), "--task", fc_task_var.get()]
            threaded(cmd, fc_output)
        else:
            from skycaptioner_v1.scripts.gradio_fusion_caption import FusionCaptioner
            struct_caption = fc_struct_text.get("1.0", "end").strip()
            if not struct_caption:
                fc_output.insert(tk.END, "Provide structural caption text or CSV file\n")
                return
            try:
                cap = FusionCaptioner(fc_model_var.get(), int(fc_tp_var.get()))
                result = cap(struct_caption, fc_task_var.get())
                fc_output.insert(tk.END, result)
            except Exception as e:
                fc_output.insert(tk.END, str(e))

    ttk.Button(fusion_tab, text="Run", command=run_fusion).grid(row=6, column=1, pady=5)


def browse_image(var):
    path = filedialog.askopenfilename()
    if path:
        var.set(path)


def browse_output(var):
    path = filedialog.askdirectory()
    if path:
        var.set(path)


from ttkthemes import ThemedTk

class SkyReelsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SkyReels Launcher")

        self.theme_var = tk.StringVar(value="equilux")
        self.root.set_theme(self.theme_var.get())

        self.script_var = tk.StringVar(value="Standard Generation")
        self.model_var = tk.StringVar(value=MODEL_OPTIONS[0])
        self.image_var = tk.StringVar()
        self.res_var = tk.StringVar(value="540P")
        self.frames_var = tk.StringVar(value="97")
        self.guidance_var = tk.StringVar(value="6.0")
        self.outdir_var = tk.StringVar(value="video_out")
        self.enhancer_var = tk.BooleanVar()
        self.prompt_enhancer_model_size_var = tk.StringVar(value="small")
        self.shift_var = tk.StringVar(value="8.0")
        self.fps_var = tk.StringVar(value="24")
        self.seed_var = tk.StringVar()
        self.offload_var = tk.BooleanVar()
        self.use_usp_var = tk.BooleanVar()
        self.teacache_var = tk.BooleanVar()
        self.teacache_thresh_var = tk.StringVar(value="0.2")
        self.use_ret_steps_var = tk.BooleanVar()
        self.video_path_var = tk.StringVar()
        self.end_image_var = tk.StringVar()
        self.ar_step_var = tk.StringVar(value="0")
        self.base_frames_var = tk.StringVar(value="97")
        self.overlap_history_var = tk.StringVar()
        self.addnoise_var = tk.StringVar(value="0")
        self.causal_block_size_var = tk.StringVar(value="1")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.LabelFrame(self.root, text="Main Options")
        main_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5, padx=5)

        ttk.Label(main_frame, text="Script").grid(row=0, column=0, sticky="w")
        ttk.Combobox(main_frame, textvariable=self.script_var, values=list(SCRIPTS.keys()), width=30).grid(
            row=0, column=1, sticky="ew"
        )

        ttk.Label(main_frame, text="Model").grid(row=1, column=0, sticky="w")
        ttk.Combobox(main_frame, textvariable=self.model_var, values=MODEL_OPTIONS, width=60).grid(
            row=1, column=1, sticky="ew"
        )

        ttk.Label(main_frame, text="Prompt").grid(row=2, column=0, sticky="nw")
        self.prompt_widget = scrolledtext.ScrolledText(main_frame, width=60, height=4)
        self.prompt_widget.grid(row=2, column=1, sticky="ew")

        ttk.Label(main_frame, text="Image").grid(row=3, column=0, sticky="w")
        img_entry = tk.Entry(main_frame, textvariable=self.image_var, width=50)
        img_entry.grid(row=3, column=1, sticky="w")
        ttk.Button(main_frame, text="Browse", command=lambda: browse_image(self.image_var)).grid(
            row=3, column=2, sticky="w"
        )

        ttk.Label(main_frame, text="Resolution").grid(row=4, column=0, sticky="w")
        ttk.Combobox(main_frame, textvariable=self.res_var, values=["540P", "720P"], width=10).grid(
            row=4, column=1, sticky="w"
        )

        ttk.Label(main_frame, text="Frames").grid(row=5, column=0, sticky="w")
        tk.Entry(main_frame, textvariable=self.frames_var, width=10).grid(row=5, column=1, sticky="w")

        ttk.Label(main_frame, text="Guidance").grid(row=6, column=0, sticky="w")
        tk.Entry(main_frame, textvariable=self.guidance_var, width=10).grid(row=6, column=1, sticky="w")

        ttk.Label(main_frame, text="Output Dir").grid(row=7, column=0, sticky="w")
        out_entry = tk.Entry(main_frame, textvariable=self.outdir_var, width=50)
        out_entry.grid(row=7, column=1, sticky="w")
        ttk.Button(main_frame, text="Browse", command=lambda: browse_output(self.outdir_var)).grid(
            row=7, column=2, sticky="w"
        )

        enhancer_frame = ttk.Frame(main_frame)
        enhancer_frame.grid(row=8, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(enhancer_frame, text="Use Prompt Enhancer", variable=self.enhancer_var).pack(side="left")

        ttk.Label(enhancer_frame, text="Model Size:").pack(side="left", padx=(10, 0))
        ttk.Combobox(
            enhancer_frame, textvariable=self.prompt_enhancer_model_size_var, values=["small", "large"], width=10
        ).pack(side="left")

        extra_frame = ttk.LabelFrame(self.root, text="Common Options")
        extra_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5, padx=5)

        ttk.Label(extra_frame, text="Shift").grid(row=0, column=0, sticky="w")
        tk.Entry(extra_frame, textvariable=self.shift_var, width=10).grid(row=0, column=1, sticky="w")

        ttk.Label(extra_frame, text="FPS").grid(row=0, column=2, sticky="w")
        tk.Entry(extra_frame, textvariable=self.fps_var, width=10).grid(row=0, column=3, sticky="w")

        ttk.Label(extra_frame, text="Seed").grid(row=1, column=0, sticky="w")
        tk.Entry(extra_frame, textvariable=self.seed_var, width=10).grid(row=1, column=1, sticky="w")

        ttk.Checkbutton(extra_frame, text="Offload", variable=self.offload_var).grid(row=1, column=2, sticky="w")
        ttk.Checkbutton(extra_frame, text="Use USP", variable=self.use_usp_var).grid(row=1, column=3, sticky="w")

        ttk.Checkbutton(extra_frame, text="Teacache", variable=self.teacache_var).grid(row=2, column=0, sticky="w")
        ttk.Label(extra_frame, text="Thresh").grid(row=2, column=1, sticky="w")
        tk.Entry(extra_frame, textvariable=self.teacache_thresh_var, width=6).grid(row=2, column=2, sticky="w")
        ttk.Checkbutton(extra_frame, text="Use Ret Steps", variable=self.use_ret_steps_var).grid(
            row=2, column=3, sticky="w"
        )

        warning_label = ttk.Label(
            extra_frame,
            text="Warning: 14B models and performance optimizations (Teacache, etc.) require significant VRAM.",
            foreground="red",
        )
        warning_label.grid(row=3, column=0, columnspan=4, sticky="w", pady=5)

        df_frame = ttk.LabelFrame(self.root, text="Diffusion Forcing Options")
        df_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5, padx=5)

        ttk.Label(df_frame, text="Video Path").grid(row=0, column=0, sticky="w")
        video_entry = tk.Entry(df_frame, textvariable=self.video_path_var, width=40)
        video_entry.grid(row=0, column=1, sticky="w")
        ttk.Button(df_frame, text="Browse", command=lambda: browse_image(self.video_path_var)).grid(
            row=0, column=2, sticky="w"
        )

        ttk.Label(df_frame, text="End Image").grid(row=1, column=0, sticky="w")
        end_entry = tk.Entry(df_frame, textvariable=self.end_image_var, width=40)
        end_entry.grid(row=1, column=1, sticky="w")
        ttk.Button(df_frame, text="Browse", command=lambda: browse_image(self.end_image_var)).grid(
            row=1, column=2, sticky="w"
        )

        ttk.Label(df_frame, text="AR Step").grid(row=2, column=0, sticky="w")
        ar_step_entry = tk.Entry(df_frame, textvariable=self.ar_step_var, width=6)
        ar_step_entry.grid(row=2, column=1, sticky="w")
        ttk.Label(df_frame, text="Base Frames").grid(row=2, column=2, sticky="w")
        base_frames_entry = tk.Entry(df_frame, textvariable=self.base_frames_var, width=6)
        base_frames_entry.grid(row=2, column=3, sticky="w")

        ttk.Label(df_frame, text="Overlap Hist").grid(row=3, column=0, sticky="w")
        overlap_entry = tk.Entry(df_frame, textvariable=self.overlap_history_var, width=6)
        overlap_entry.grid(row=3, column=1, sticky="w")
        ttk.Label(df_frame, text="Addnoise").grid(row=3, column=2, sticky="w")
        addnoise_entry = tk.Entry(df_frame, textvariable=self.addnoise_var, width=6)
        addnoise_entry.grid(row=3, column=3, sticky="w")

        ttk.Label(df_frame, text="Causal Block").grid(row=4, column=0, sticky="w")
        causal_entry = tk.Entry(df_frame, textvariable=self.causal_block_size_var, width=6)
        causal_entry.grid(row=4, column=1, sticky="w")

        self.df_widgets = [
            video_entry,
            end_entry,
            ar_step_entry,
            base_frames_entry,
            overlap_entry,
            addnoise_entry,
            causal_entry,
        ]

        self.script_var.trace_add("write", self.update_fields)
        self.update_fields()

        self.output = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.output.grid(row=12, column=0, columnspan=4, pady=5)

        try:
            import diffusers  # noqa: F401
            import decord  # noqa: F401
            packages_installed = True
        except Exception:
            packages_installed = False

        button_state = "normal" if packages_installed else "disabled"

        self.run_button = ttk.Button(
            self.root,
            text="Run",
            command=self.run_generation,
            state=button_state,
        )
        self.run_button.grid(row=11, column=1, pady=5)

        self.cancel_button = ttk.Button(
            self.root,
            text="Cancel",
            command=self.cancel_process,
            state="disabled",
        )
        self.cancel_button.grid(row=11, column=2, pady=5)

        self.enhancer_button = ttk.Button(
            self.root,
            text="Prompt Enhancer",
            command=lambda: open_prompt_enhancer(self.prompt_widget),
            state=button_state,
        )
        self.enhancer_button.grid(row=11, column=2, pady=5)

        self.caption_button = ttk.Button(
            self.root,
            text="Captioner",
            command=open_captioner,
            state=button_state,
        )
        self.caption_button.grid(row=11, column=3, pady=5)

        ttk.Button(
            self.root,
            text="Install Dependencies",
            command=lambda: install_deps(self.output, self.run_button, self.enhancer_button, self.caption_button),
        ).grid(row=11, column=0, pady=5)

        ttk.Button(self.root, text="Quit", command=self.root.destroy).grid(row=11, column=4, pady=5)

        self.create_theme_menu()

    def create_theme_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=theme_menu)

        for theme in sorted(self.root.get_themes()):
            theme_menu.add_radiobutton(label=theme, variable=self.theme_var, command=self.set_theme)

        theme_menu.add_separator()
        theme_menu.add_checkbutton(label="Dark Mode", onvalue="equilux", offvalue="arc", variable=self.theme_var, command=self.set_theme)

    def set_theme(self):
        self.root.set_theme(self.theme_var.get())

    def update_fields(self, *_):
        state = "normal" if self.script_var.get() == "Diffusion Forcing" else "disabled"
        for w in self.df_widgets:
            w.configure(state=state)

    def run_generation(self):
        self.run_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        run_generation(
            self,
            self.script_var,
            self.model_var,
            self.prompt_widget,
            self.image_var,
            self.res_var,
            self.frames_var,
            self.guidance_var,
            self.outdir_var,
            self.enhancer_var,
            self.prompt_enhancer_model_size_var,
            self.shift_var,
            self.fps_var,
            self.seed_var,
            self.offload_var,
            self.use_usp_var,
            self.teacache_var,
            self.teacache_thresh_var,
            self.use_ret_steps_var,
            self.video_path_var,
            self.end_image_var,
            self.ar_step_var,
            self.base_frames_var,
            self.overlap_history_var,
            self.addnoise_var,
            self.causal_block_size_var,
            self.output,
        )

    def cancel_process(self):
        if hasattr(self, "process") and self.process.poll() is None:
            self.process.terminate()
            self.output.insert(tk.END, "\nProcess cancelled by user.\n")
            self.cancel_button.config(state="disabled")
            self.run_button.config(state="normal")


def main():
    root = ThemedTk(theme="equilux")
    app = SkyReelsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
