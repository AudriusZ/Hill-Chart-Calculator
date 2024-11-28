import os

# Define the UI files
ui_files = ['src/turbine_simulator_window.ui', 'src/manual-automatic_control_widget.ui']
output_file = 'src/turbine_simulator_gui.py'

# Convert .ui files to .py and combine them
with open(output_file, 'w') as outfile:
    for ui_file in ui_files:
        py_file = ui_file.replace('.ui', '.py')
        # Run pyuic6 with -x flag
        os.system(f"pyuic6 -x {ui_file} -o {py_file}")
        
        # Append the generated .py content to the combined file
        with open(py_file, 'r') as infile:
            outfile.write(infile.read())
            outfile.write('\n\n')  # Add spacing between files
            
        # Optionally, remove individual .py files after combining
        os.remove(py_file)

print(f"Combined UI written to {output_file}")

