#To create standalon exe use the line below:
#pyinstaller.exe --onefile Calculator.py -w
from tkinter import *
from SingleCurve import SingleCurve

def create_checkbox(text, value):
    var = IntVar()
    chk = Checkbutton(top, text=text, variable=var, onvalue=value, offvalue=0, command=update_count)
    chk.pack(anchor=W)
    checkbox_vars.append(var)
    checkboxes.append(chk)

def update_count():
    selected_values = [var.get() for var in checkbox_vars if var.get() != 0]
    selected_count = len(selected_values)        
    if selected_count == 2:
        for var, chk in zip(checkbox_vars, checkboxes):
            if var.get() == 0:
                chk.config(state='disabled')
        next_button.config(state='normal')
    else:
        for chk in checkboxes:
            chk.config(state='normal')
        next_button.config(state='disabled')

def set_inputs():
    selected_values = [var.get() for var in checkbox_vars if var.get() != 0]        
    var_entry_1.config(state='normal')
    var_entry_2.config(state='normal')
    var_label_1.config(text=options[selected_values[0]-1])
    var_label_2.config(text=options[selected_values[1]-1])
    calculate_button.config(state='normal')

def calculate():
    #this is where the calculation will take place
    selected_values = [var.get() for var in checkbox_vars if var.get() != 0]
    var1 = float(var_entry_1.get())
    var2 = float(var_entry_2.get())
    testCalculation = SingleCurve(selected_values,options,var1,var2)
    testCalculation.get_BEP_values()
    testCalculation.cases()
    H,Q,n,D,Efficiency,Power = testCalculation.return_values()
    
    # Clear previous results
    result_text.delete(1.0, END)
    
    # Display the results in the text box
    result_text.insert(END, options[0] + ' = {:.2f}\n'.format(H))
    result_text.insert(END, options[1] + ' = {:.2f}\n'.format(Q))
    result_text.insert(END, options[2] + ' = {:.2f}\n'.format(n))
    result_text.insert(END, options[3] + ' = {:.2f}\n'.format(D))
    result_text.insert(END, 'Efficiency η [-]= {:.2f}\n'.format(Efficiency))
    result_text.insert(END, 'Power P [W] = {:.0f}\n'.format(Power))

    #print(H,Q,n,D)
    #print(options[0],'=',H)
    #print(options[1],'=',Q)
    #print(options[2],'=',n)
    #print(options[3],'=',D)
    
  

top = Tk()  
top.title('Hill Chart Calculator')
top.geometry("350x350") 

checkbox_vars = []
checkboxes = []

lbl = Label(text="Select two paramenters and press Next:")  
lbl.pack()  

options = ["Head H [m]", "Flow rate Q [m^3/s]", "Rotational speed n [rpm]", "Runner diameter D [m]"]
values = [1, 2, 3, 4]

for option, value in zip(options, values):
    create_checkbox(option, value)

next_button = Button(top, text="Next", command=set_inputs, state='disabled')
next_button.pack()

var_label_1 = Label(top, text="Input value 1")
var_label_1.pack()
var_entry_1 = Entry(top, state='disabled')
var_entry_1.pack()
var_label_2 = Label(top, text="Input value 2")
var_label_2.pack()
var_entry_2 = Entry(top, state='disabled')
var_entry_2.pack()

calculate_button = Button(top, text="Calculate", command=calculate, state='disabled')
calculate_button.pack()

result_text = Text(top, height=10, width=40)
result_text.pack()

top.mainloop()