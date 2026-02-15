import os, sys

sys.path.insert(0, os.path.abspath("src"))
import tkinter as tk
from hiro_ust.hiro_ust_dev import USTGeneratorApp

root = tk.Tk()
app = USTGeneratorApp(root)
# configure
app.ustx_mode_var.set(True) if hasattr(app, "ustx_mode_var") else None
app.project_var.set("DebugViaDev")
app.lyrics_text.delete("1.0", "end")
app.lyrics_text.insert(
    "1.0",
    "きゃっきゃ うれし いたい さぶり ゆびさき きりさけ あかい つゆ\nいたみ いたみ きもちいい うたをうたいましょう らららら",
)
app.tempo_var.set("120")
# call
res = app._generate_content()
print("RESULT_TYPE:", type(res))
print("LEN:", len(res) if res else None)
# destroy root
root.destroy()
