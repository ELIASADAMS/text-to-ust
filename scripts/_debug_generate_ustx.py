from hiro_ust.cli import main

# Initialize GUI in debug mode (no mainloop)
app = main(debug=True)

# Prepare fields to generate USTX
try:
    # Ensure USTX mode enabled
    if hasattr(app, 'ustx_mode_var'):
        app.ustx_mode_var.set(True)
    else:
        # create one if missing
        import tkinter as tk
        app.ustx_mode_var = tk.BooleanVar(value=True)

    app.project_var.set('DebugProject')
    app.lyrics_text.delete('1.0', 'end')
    app.lyrics_text.insert('1.0', 'きゃっきゃ うれし')
    app.tempo_var.set('120')
    app.length_var.set('240')
    app.line_pause_var.set('960')
    app.section_pause_var.set('1920')
    app.length_var_ctrl.set('0.3')
    app.stretch_var.set('0.25')
    app.pre_utter_var.set('25')
    app.voice_overlap_var.set('10')
    app.intensity_base_var.set('80')
    app.envelope_var.set('Pop')
    app.voice_var.set(list(app.voice_var['values'])[0])
    app.scale_var.set(list(app.scale_var['values'])[0])

    # Call generation
    ust_content = app._generate_content()
    if ust_content is None:
        print('Result: None (likely validation failed)')
    else:
        print('USTX length:', len(ust_content))
        print(ust_content[:800])
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

