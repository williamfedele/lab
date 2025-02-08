class SettingsWindow:
    def __init__(self, config, save_callback):
        self.window = tk.Tk()
        self.window.title("Text Assistant Settings")
        self.window.geometry("400x500")
        self.config = config
        self.save_callback = save_callback

        # Create main frame with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # LLM Provider Settings
        self.create_provider_settings(main_frame)

        # Model Settings
        self.create_model_settings(main_frame)

        # Shortcut Settings
        self.create_shortcut_settings(main_frame)

        # Behavior Settings
        self.create_behavior_settings(main_frame)

        # Save Button
        save_button = ttk.Button(
            main_frame, text="Save Settings", command=self.save_settings
        )
        save_button.grid(row=20, column=0, columnspan=2, pady=20)

        # Center window on screen
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.window.winfo_width()) // 2
        y = (screen_height - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")

    def create_provider_settings(self, parent):
        # Provider Frame
        provider_frame = ttk.LabelFrame(parent, text="LLM Provider", padding="10")
        provider_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Provider Selection
        ttk.Label(provider_frame, text="Provider:").grid(row=0, column=0, sticky=tk.W)
        self.provider_var = tk.StringVar(value="anthropic")
        providers = ttk.Combobox(provider_frame, textvariable=self.provider_var)
        providers["values"] = ("anthropic", "openai", "custom")
        providers.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # API Key
        ttk.Label(provider_frame, text="API Key:").grid(row=1, column=0, sticky=tk.W)
        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        api_key_entry = ttk.Entry(
            provider_frame, textvariable=self.api_key_var, show="*"
        )
        api_key_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        # API URL
        ttk.Label(provider_frame, text="API URL:").grid(row=2, column=0, sticky=tk.W)
        self.api_url_var = tk.StringVar(value=self.config.get("api_url", ""))
        api_url_entry = ttk.Entry(provider_frame, textvariable=self.api_url_var)
        api_url_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))

    def create_model_settings(self, parent):
        # Model Frame
        model_frame = ttk.LabelFrame(parent, text="Model Settings", padding="10")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Model Selection
        ttk.Label(model_frame, text="Model:").grid(row=0, column=0, sticky=tk.W)
        self.model_var = tk.StringVar(
            value=self.config.get("model", "claude-3-sonnet-20240229")
        )
        model_entry = ttk.Entry(model_frame, textvariable=self.model_var)
        model_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Max Tokens
        ttk.Label(model_frame, text="Max Tokens:").grid(row=1, column=0, sticky=tk.W)
        self.max_tokens_var = tk.StringVar(
            value=str(self.config.get("max_tokens", 1000))
        )
        max_tokens_entry = ttk.Entry(model_frame, textvariable=self.max_tokens_var)
        max_tokens_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

    def create_shortcut_settings(self, parent):
        # Shortcut Frame
        shortcut_frame = ttk.LabelFrame(parent, text="Shortcut Settings", padding="10")
        shortcut_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Activation Shortcut
        ttk.Label(shortcut_frame, text="Activation Shortcut:").grid(
            row=0, column=0, sticky=tk.W
        )
        self.shortcut_var = tk.StringVar(
            value=self.config.get("shortcut", "ctrl+shift+space")
        )
        shortcut_entry = ttk.Entry(shortcut_frame, textvariable=self.shortcut_var)
        shortcut_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

    def create_behavior_settings(self, parent):
        # Behavior Frame
        behavior_frame = ttk.LabelFrame(parent, text="Behavior Settings", padding="10")
        behavior_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # Direct Insertion Toggle
        self.direct_insertion_var = tk.BooleanVar(
            value=self.config.get("use_direct_insertion", True)
        )
        direct_insertion_check = ttk.Checkbutton(
            behavior_frame,
            text="Use direct cursor insertion (when available)",
            variable=self.direct_insertion_var,
        )
        direct_insertion_check.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # System Tray Behavior
        self.minimize_to_tray_var = tk.BooleanVar(
            value=self.config.get("minimize_to_tray", True)
        )
        minimize_to_tray_check = ttk.Checkbutton(
            behavior_frame,
            text="Minimize to system tray",
            variable=self.minimize_to_tray_var,
        )
        minimize_to_tray_check.grid(row=1, column=0, columnspan=2, sticky=tk.W)

    def save_settings(self):
        new_config = {
            "api_key": self.api_key_var.get(),
            "api_url": self.api_url_var.get(),
            "model": self.model_var.get(),
            "max_tokens": int(self.max_tokens_var.get()),
            "shortcut": self.shortcut_var.get(),
            "use_direct_insertion": self.direct_insertion_var.get(),
            "minimize_to_tray": self.minimize_to_tray_var.get(),
        }

        self.save_callback(new_config)
        messagebox.showinfo("Success", "Settings saved successfully!")
        self.window.destroy()
