import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import sys
from translate_executor import translate_ja_to_en, translate_eng_to_jpn
from history_manager import HistoryManager

class TranslateGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("翻訳ツール")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(script_dir, "config.json")
        self.history_path = os.path.join(script_dir, "translation_history.json")

        self.history_manager = HistoryManager(self.config_path, self.history_path)

        config = self.history_manager.config
        self.geometry(f"{config.get('window_width', 900)}x{config.get('window_height', 700)}")

        self.setup_layout()

    def setup_layout(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(left_frame, text="日本語", font=("Arial", 12, "bold")).pack()
        self.jpn_text = scrolledtext.ScrolledText(left_frame, height=15, width=40, wrap=tk.WORD)
        self.jpn_text.pack(fill=tk.BOTH, expand=True)
        tk.Button(left_frame, text="クリップボードにコピー", command=self.copy_jpn).pack(pady=5)

        center_frame = tk.Frame(top_frame)
        center_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(center_frame, text="Jpn⇒Eng", command=self.on_jpn_to_eng, width=10, height=2).pack(pady=10)
        tk.Button(center_frame, text="Eng⇒Jpn", command=self.on_eng_to_jpn, width=10, height=2).pack(pady=10)

        right_frame = tk.Frame(top_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(right_frame, text="英語", font=("Arial", 12, "bold")).pack()
        self.eng_text = scrolledtext.ScrolledText(right_frame, height=15, width=40, wrap=tk.WORD)
        self.eng_text.pack(fill=tk.BOTH, expand=True)
        tk.Button(right_frame, text="クリップボードにコピー", command=self.copy_eng).pack(pady=5)

        history_frame = tk.Frame(main_frame)
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        tk.Label(history_frame, text="直前の翻訳履歴", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.history_listbox = tk.Listbox(history_frame, height=5, width=80)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        self.refresh_history()

    def on_jpn_to_eng(self):
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
            messagebox.showinfo("完了", "日本語をコピーしました")
        else:
            messagebox.showwarning("警告", "コピーするテキストがありません")

    def copy_eng(self):
        text = self.eng_text.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("完了", "英語をコピーしました")
        else:
            messagebox.showwarning("警告", "コピーするテキストがありません")

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

if __name__ == "__main__":
    app = TranslateGUI()
    app.mainloop()
