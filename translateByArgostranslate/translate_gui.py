import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import sys
import threading
import ctypes
from translate_executor import translate_ja_to_en, translate_eng_to_jpn, check_models_installed, download_models, reset_models, preload_models
from history_manager import HistoryManager

class TranslateGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("translatetool.1.0")
        self.title("オフライン翻訳ツール")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "app_icon.ico")
        self.iconbitmap(icon_path)
        self.config_path = os.path.join(script_dir, "config.json")
        self.history_path = os.path.join(script_dir, "translation_history.json")

        self.history_manager = HistoryManager(self.config_path, self.history_path)

        config = self.history_manager.config
        self.geometry(f"{config.get('window_width', 900)}x{config.get('window_height', 700)}")

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.setup_layout()

    def setup_layout(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        config_frame = tk.Frame(main_frame)
        config_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(config_frame, text="フォントサイズ:").pack(side=tk.LEFT, padx=(0, 10))
        self.font_size_scale = tk.Scale(config_frame, from_=8, to=20, orient=tk.HORIZONTAL,
                                        command=self.on_font_size_change, length=150)
        self.font_size_scale.set(self.history_manager.config.get('font_size', 12))
        self.font_size_scale.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(config_frame, text="履歴保持件数:").pack(side=tk.LEFT, padx=(0, 5))
        self.history_max_var = tk.StringVar(value=str(self.history_manager.config.get('history_max_items', 10)))
        self.history_max_spinbox = tk.Spinbox(config_frame, from_=1, to=100, width=5,
                                             textvariable=self.history_max_var, command=self.on_history_max_change)
        self.history_max_spinbox.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(config_frame, text="件").pack(side=tk.LEFT)

        model_frame = tk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=(0, 10))

        self.model_status_label = tk.Label(model_frame, text="モデル: 確認中...", fg="gray")
        self.model_status_label.pack(side=tk.LEFT, padx=(0, 10))

        self.download_button = tk.Button(model_frame, text="モデルをダウンロード", command=self.on_download_models, width=20)
        self.download_button.pack(side=tk.LEFT, padx=(0, 5))

        self.reset_button = tk.Button(model_frame, text="モデルをリセット", command=self.on_reset_models, width=15)
        self.reset_button.pack(side=tk.LEFT, padx=(0, 5))

        self.update_model_status()

        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(left_frame, text="日本語", font=("Segoe UI", 12, "bold")).pack()
        self.jpn_text = scrolledtext.ScrolledText(left_frame, height=15, width=40, wrap=tk.WORD)
        self.jpn_text.pack(fill=tk.BOTH, expand=True)

        jpn_button_frame = tk.Frame(left_frame)
        jpn_button_frame.pack(fill=tk.X, pady=5)
        tk.Button(jpn_button_frame, text="コピー", command=self.copy_jpn, width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(jpn_button_frame, text="クリア", command=self.clear_jpn, width=15).pack(side=tk.LEFT, padx=2)

        center_frame = tk.Frame(top_frame)
        center_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(center_frame, text="Jpn⇒Eng", command=self.on_jpn_to_eng, width=10, height=2).pack(pady=10)
        tk.Button(center_frame, text="Eng⇒Jpn", command=self.on_eng_to_jpn, width=10, height=2).pack(pady=10)

        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(right_frame, text="英語", font=("Segoe UI", 12, "bold")).pack()
        self.eng_text = scrolledtext.ScrolledText(right_frame, height=15, width=40, wrap=tk.WORD)
        self.eng_text.pack(fill=tk.BOTH, expand=True)

        eng_button_frame = tk.Frame(right_frame)
        eng_button_frame.pack(fill=tk.X, pady=5)
        tk.Button(eng_button_frame, text="コピー", command=self.copy_eng, width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(eng_button_frame, text="クリア", command=self.clear_eng, width=15).pack(side=tk.LEFT, padx=2)

        history_frame = tk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        history_header_frame = tk.Frame(history_frame)
        history_header_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(history_header_frame, text="直前の翻訳履歴", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        tk.Button(history_header_frame, text="履歴クリア", command=self.on_clear_history, width=15).pack(side=tk.RIGHT, padx=(5, 0))
        self.history_listbox = tk.Listbox(history_frame, height=5, width=80)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        self.refresh_history()
        self.preload_models_async()

    def on_jpn_to_eng(self):
        if not check_models_installed():
            messagebox.showwarning("モデル未インストール", "モデルをダウンロードしてください")
            return

        try:
            source = self.jpn_text.get("1.0", tk.END).strip()
            if not source:
                messagebox.showwarning("警告", "日本語を入力してください")
                return
            result = translate_ja_to_en(source)
            self.eng_text.delete("1.0", tk.END)
            self.eng_text.insert("1.0", result)
            self.history_manager.add_history(source, result, "jpn_to_eng")
            self.refresh_history()
        except Exception as e:
            messagebox.showerror("エラー", f"翻訳に失敗しました: {e}")

    def on_eng_to_jpn(self):
        if not check_models_installed():
            messagebox.showwarning("モデル未インストール", "モデルをダウンロードしてください")
            return

        try:
            source = self.eng_text.get("1.0", tk.END).strip()
            if not source:
                messagebox.showwarning("警告", "英語を入力してください")
                return
            result = translate_eng_to_jpn(source)
            self.jpn_text.delete("1.0", tk.END)
            self.jpn_text.insert("1.0", result)
            self.history_manager.add_history(source, result, "eng_to_jpn")
            self.refresh_history()
        except Exception as e:
            messagebox.showerror("エラー", f"翻訳に失敗しました: {e}")

    def copy_jpn(self):
        text = self.jpn_text.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)

    def copy_eng(self):
        text = self.eng_text.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)

    def refresh_history(self):
        self.history_listbox.delete(0, tk.END)
        for item in self.history_manager.get_latest():
            direction_label = "Jpn→Eng" if item["direction"] == "jpn_to_eng" else "Eng→Jpn"
            display_text = f"{direction_label}: {item['source'][:30]}... ⇒ {item['translation'][:30]}..."
            self.history_listbox.insert(tk.END, display_text)

    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            item = self.history_manager.get_latest()[idx]
            if item["direction"] == "jpn_to_eng":
                self.jpn_text.delete("1.0", tk.END)
                self.jpn_text.insert("1.0", item["source"])
                self.eng_text.delete("1.0", tk.END)
                self.eng_text.insert("1.0", item["translation"])
            else:
                self.eng_text.delete("1.0", tk.END)
                self.eng_text.insert("1.0", item["source"])
                self.jpn_text.delete("1.0", tk.END)
                self.jpn_text.insert("1.0", item["translation"])

    def clear_jpn(self):
        self.jpn_text.delete("1.0", tk.END)

    def clear_eng(self):
        self.eng_text.delete("1.0", tk.END)

    def on_font_size_change(self, value):
        font_size = int(value)
        font = ("Segoe UI", font_size, "normal")
        self.jpn_text.config(font=font)
        self.eng_text.config(font=font)

    def on_history_max_change(self):
        try:
            max_items = int(self.history_max_var.get())
            if max_items < 1:
                max_items = 1
                self.history_max_var.set("1")
            self.history_manager.config['history_max_items'] = max_items
            self.history_manager.save_config()
        except ValueError:
            pass

    def on_clear_history(self):
        if messagebox.askyesno("確認", "翻訳履歴を削除してもよろしいですか？"):
            self.history_manager.clear_history()
            self.refresh_history()

    def update_model_status(self):
        try:
            if check_models_installed():
                self.model_status_label.config(text="モデル: ✓ インストール済み", fg="green")
                self.download_button.config(state=tk.DISABLED)
            else:
                self.model_status_label.config(text="モデル: ⚠ 未インストール", fg="red")
                self.download_button.config(state=tk.NORMAL)
        except Exception as e:
            self.model_status_label.config(text=f"モデル: エラー ({str(e)[:20]})", fg="red")

    def on_download_models(self):
        self.download_button.config(state=tk.DISABLED, text="ダウンロード中...")
        threading.Thread(target=self._download_models_thread, daemon=True).start()

    def _download_models_thread(self):
        try:
            download_models()
            self.model_status_label.config(text="モデル: ✓ インストール済み", fg="green")
            messagebox.showinfo("完了", "モデルのダウンロードが完了しました")
        except Exception as e:
            messagebox.showerror("エラー", f"ダウンロードに失敗しました: {e}")
        finally:
            self.download_button.config(state=tk.NORMAL, text="モデルをダウンロード")
            self.update_model_status()

    def on_reset_models(self):
        if not messagebox.askyesno("確認", "モデルをリセットしますか？\nモデルをダウンロードし直す必要があります。"):
            return

        self.reset_button.config(state=tk.DISABLED, text="リセット中...")
        threading.Thread(target=self._reset_models_thread, daemon=True).start()

    def _reset_models_thread(self):
        try:
            reset_models()
            self.model_status_label.config(text="モデル: ⚠ 未インストール", fg="red")
            messagebox.showinfo("完了", "モデルをリセットしました")
        except Exception as e:
            messagebox.showerror("エラー", f"リセットに失敗しました: {e}")
        finally:
            self.reset_button.config(state=tk.NORMAL, text="モデルをリセット")
            self.update_model_status()

    def preload_models_async(self):
        threading.Thread(target=self._preload_models_thread, daemon=True).start()

    def _preload_models_thread(self):
        preload_models()

    def _on_closing(self):
        font_size = int(self.font_size_scale.get())
        self.history_manager.config['font_size'] = font_size
        self.history_manager.save_config()
        self.destroy()

if __name__ == "__main__":
    app = TranslateGUI()
    app.mainloop()
