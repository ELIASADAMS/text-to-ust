from hiro_ust.cli import main
import os

app = main(debug=True)
# configure
app.ustx_mode_var.set(True) if hasattr(app, "ustx_mode_var") else None
name = "CheckSaveDebug"
app.project_var.set(name)
app.lyrics_text.delete("1.0", "end")
app.lyrics_text.insert(
    "1.0",
    "きゃっきゃ うれし いたい さぶり ゆびさき きりさけ あかい つゆ\nいたみ いたみ きもちいい うたをうたいましょう らららら",
)
# generate
app.generate_ust()
# file path
import sys

if getattr(sys, "frozen", False):
    save_dir = os.path.dirname(sys.executable)
else:
    save_dir = os.path.dirname(os.path.abspath(__file__))
extn = ".ustx" if hasattr(app, "ustx_mode_var") and app.ustx_mode_var.get() else ".ust"
filename = os.path.join(save_dir, f"{name}{extn}")
print("Expect file at:", filename)
print("Exists:", os.path.exists(filename))
if os.path.exists(filename):
    print("Size bytes:", os.path.getsize(filename))
    with open(filename, "r", encoding="utf-8-sig") as f:
        print("Head:", f.read(400))
else:
    print("No file saved")
