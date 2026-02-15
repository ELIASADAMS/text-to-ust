from hiro_ust.cli import main

app = main(debug=True)
print("APP:", app)
print("TYPE:", type(app))
print("HAS _generate_content:", hasattr(app, "_generate_content"))
print("has attributes:", [a for a in dir(app) if not a.startswith("_")][:40])
