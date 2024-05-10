class SingleCurve:

    def __init__(self, selected_values, options, var1, var2):
        
        self.selected_values = selected_values
        self.options = options
        self.var1 = var1
        self.var2 = var2
        self.H = 0
        self.Q = 0
        self.n = 0
        self.D = 0
        self.Q11 = 0
        self.n11 = 0
        self.efficiency = 0
        self.power = 0

    def get_BEP_values(self):
        self.Q11 = 0.876
        self.n11 = 127.609
        self.efficiency = 0.820
    
    def cases(self):
        #print(self.selected_values)
        if self.selected_values ==[1,2]:
            # Case 1
            #print("Case H and Q Inputs")      
            self.H = self.var1
            self.Q = self.var2
            self.D = (self.Q/(self.Q11*(self.H)**0.5))**0.5
            self.n = (self.H**0.5) * self.n11/self.D
        
        elif self.selected_values ==[1,3]:
            # Case 2
            #print("Case H and n")
            self.H = self.var1
            self.n = self.var2
            self.D = (self.H**0.5) * self.n11 / self.n
            self.Q = self.D**2 * self.Q11 * (self.H**0.5)
            
        
        elif self.selected_values ==[1,4]:
            # Case 3: H and D Inputs
            #print("Case H and D")
            self.H = self.var1
            self.D = self.var2
            self.n = (self.H ** 0.5) * self.n11 / self.D
            self.Q = self.D ** 2 * self.Q11 * (self.H ** 0.5)

        elif self.selected_values ==[2,3]:
            # Case 4: Q and n Inputs
            #print("Case Q and n")
            self.Q = self.var1
            self.n = self.var2
            self.D = (self.Q*self.n11/(self.Q11*self.n))**(1/3)
            self.H = (self.n*self.D/self.n11)**2

        elif self.selected_values ==[2,4]:
            # Case 5: Q and D Inputs
            #print("Case Q and D")
            self.Q = self.var1
            self.D = self.var2
            self.H = (self.Q / (self.Q11 * (self.D ** 2))) ** 2
            self.n = (self.H ** 0.5) * self.n11 / self.D

        elif self.selected_values ==[3,4]:
            # Case 6: n and D Inputs
            #print("Case n and D")
            self.n = self.var1
            self.D = self.var2
            self.H = (self.n * self.D / self.n11) ** 2
            self.Q = self.D ** 2 * self.Q11 * (self.H ** 0.5)
        
        else:
            # Default case
            print("Default case")

        self.power = self.Q * self.H * 1000*9.8 * self.efficiency
        #     
    def return_values(self):
        return self.H, self.Q, self.n, self.D, self.efficiency, self.power