from math import sqrt
from numpy import array,zeros,copy,delete
from numpy.linalg import solve
from functions import cellStyle
from openpyxl import Workbook

class Section():
    def __init__(self,name,elasticity_mod=1.00,area=1.00,inertia=1.00):
        """Crea una sección con sus propiedades básicas.
        
        Parameters
        ----------
        name : str
            Nombre de la sección.
        elasticity_mod : float
            Módulo de elasticidad.
        area : float
            Área de la sección transversal.
        inertia : float
            Momento de inercia de la sección.
        """
        self.name = name
        self.E = elasticity_mod
        self.A = area
        self.I = inertia

class Joint():
    """Crea un nudo.

    Parametros
    ----------
    x : float
        Coordenada X del nudo.
    y : float
        Coordenada Y del nudo.
    name : str
        Nombre del nudo.
    """
    def __init__(self,x,y,name):
        self.x = x
        self.y = y
        self.name = name
        self.GdL = []
        self.is_used = False
    def use(self,lista_GdL):
        self.is_used = True
        self.GdL = lista_GdL

class TrussElement():
    """
    Crea un elemento barra biarticulado, 4 grados de libertad, 2 en cada nudo

    Parameters
    ----------
    Ji : Joint object
        Nudo inicial del elemento.
    Jf : Join object
        Nudo final del elemento.
    section : Section object
        Sección del elemento.
    name : str
        Nombre del elemento.
    """
    def __init__(self,Ji,Jf,section,name):   # Ji y Jf son objetos de la clase Joint()
        self.name = name
        # Asignamos las propiedades de sección
        self.section = section.name
        self.A = section.A
        self.E = section.E
        # Asignamos las propiedades geométricas       
        self.Ji = Ji.name   # Guarda el nombre del nudo inicial
        self.Jf = Jf.name   # Guarda el nombre del nudo final
        self.Xi = Ji.x
        self.Xf = Jf.x
        self.Yi = Ji.y
        self.Yf = Jf.y
        self.Δx = Jf.x - Ji.x   # Calcula el delta de x
        self.Δy = Jf.y - Ji.y   # Calcula el delta de y
        self.L = sqrt(self.Δx**2 + self.Δy**2)      # Calcula la longitud del elemento
        if self.L != 0:
            self.cx = self.Δx / self.L
            self.cy = self.Δy / self.L
            self.t_matrix = array([[ self.cx, self.cy, 0, 0], [ 0, 0, self.cx, self.cy]])
            P = self.E * self.A / self.L
            self.k_loc = array([[ P, -P], [-P, P]])
            self.k_glob = self.t_matrix.T @ self.k_loc @ self.t_matrix
        else: print(f"Error, elemento {name} tiene longitud 0.")
    def assignGDL(self,GdL):
        """
        Asigna los grados de libertad globales del elemento.
        
        Parameters
        ----------
        GdL : list
            Lista de los grados de libertad.
        """
        self.GdL = GdL
    def deform(self,U):
        self.u_g = zeros((4,1))
        for i in range(4):
            self.u_g[i] = U[self.GdL[i]]
        self.u_l = self.t_matrix @ self.u_g
        self.f_g = self.k_glob @ self.u_g
        self.f_l = self.t_matrix @ self.f_g

    def elemento_excel(self,sheet,c,r):
        cellStyle(sheet,col=c,ren=r,val=self.name,mergeCell=c+6,color="00FFFF",aline=True,bold=True)
        
        cellStyle(sheet,col=c,ren=r+2,val="Joint",color="99CCFF",aline=True,bold=True)
        cellStyle(sheet,col=c+1,ren=r+2,val=f"X",color="99CCFF",aline=True,bold=True)
        cellStyle(sheet,col=c+2,ren=r+2,val=f"Y",color="99CCFF",aline=True,bold=True)
        cellStyle(sheet,col=c,ren=r+3,val=self.Ji,color="CCECFF",aline=True)
        cellStyle(sheet,col=c,ren=r+4,val=self.Jf,color="CCECFF",aline=True)
        cellStyle(sheet,col=c+1,ren=r+3,val=self.Xi,color="CCECFF",aline=True)
        cellStyle(sheet,col=c+1,ren=r+4,val=self.Xf,color="CCECFF",aline=True)
        cellStyle(sheet,col=c+2,ren=r+3,val=self.Yi,color="CCECFF",aline=True)
        cellStyle(sheet,col=c+2,ren=r+4,val=self.Yf,color="CCECFF",aline=True)

        cellStyle(sheet,col=c,ren=r+5,val=f"L",color="99CCFF",aline=True,bold=True)
        cellStyle(sheet,col=c+1,ren=r+5,val="cx",color="99CCFF",aline=True,bold=True)
        cellStyle(sheet,col=c+2,ren=r+5,val="cy",color="99CCFF",aline=True,bold=True)
        cellStyle(sheet,col=c,ren=r+6,val=self.L,color="CCECFF",aline=True)
        cellStyle(sheet,col=c+1,ren=r+6,val=self.cx,color="CCECFF",aline=True)
        cellStyle(sheet,col=c+2,ren=r+6,val=self.cy,color="CCECFF",aline=True)

        cellStyle(sheet,col=c+4,ren=r+2,val="Section",color="00CC99",aline=True,bold=True)
        cellStyle(sheet,col=c+5,ren=r+2,val=f"E",color="00CC99",aline=True,bold=True)
        cellStyle(sheet,col=c+6,ren=r+2,val=f"A",color="00CC99",aline=True,bold=True)
        cellStyle(sheet,col=c+4,ren=r+3,val=self.section,color="BDFFEE",aline=True)
        cellStyle(sheet,col=c+5,ren=r+3,val=self.E,color="BDFFEE",aline=True)
        cellStyle(sheet,col=c+6,ren=r+3,val=self.A,color="BDFFEE",aline=True)

        cellStyle(sheet,col=c,ren=r+8,val="Transformation Matrix",mergeCell=c+3,color="FF7C80",aline=True,bold=True)
        for i in range(2):
            for j in range(4):
                cellStyle(sheet,col=c+j,ren=r+9+i,val=self.t_matrix[i,j],color="FFD9DA",aline=True)
        
        cellStyle(sheet,col=c+5,ren=r+8,val="Local Stiffness Matrix",mergeCell=c+6,color="D88BFF",aline=True,bold=True)
        for i in range(2):
            for j in range(2):
                cellStyle(sheet,col=c+5+j,ren=r+9+i,val=self.k_loc[i,j],color="F1D5FF",aline=True)
        
        cellStyle(sheet,col=c,ren=r+12,val="In Global Axes",mergeCell=c+6,color="FFFF00",aline=True,bold=True)

        cellStyle(sheet,col=c,ren=r+13,val="Element Global Stiffness Matrix",mergeCell=c+4,color="D88BFF",aline=True,bold=True)
        cellStyle(sheet,col=c,ren=r+14,val="DoF",color="E8B9FF",aline=True,bold=True)
        for i in range(4):
            cellStyle(sheet,col=c+1+i,ren=r+14,val=self.GdL[i],color="E8B9FF",aline=True,bold=True)
            cellStyle(sheet,col=c,ren=r+15+i,val=self.GdL[i],color="E8B9FF",aline=True,bold=True)
        for i in range(4):
            for j in range(4):
                cellStyle(sheet,col=c+1+j,ren=r+15+i,val=self.k_glob[i,j],color="F1D5FF",aline=True)
        
        cellStyle(sheet,col=c+5,ren=r+13,val="Disp.",color="00FFCC",aline=True,bold=True)
        cellStyle(sheet,col=c+6,ren=r+13,val="Forces",color="00FFCC",aline=True,bold=True)
        for i in range(4):
            cellStyle(sheet,col=c+5,ren=r+15+i,val=self.u_g[i,0],color="9BFFEC",aline=True)
        for i in range(4):
            cellStyle(sheet,col=c+6,ren=r+15+i,val=self.f_g[i,0],color="9BFFEC",aline=True)

        cellStyle(sheet,col=c+4,ren=r+4,val="In Local Axes",mergeCell=c+6,color="FFFF00",aline=True,bold=True)
        cellStyle(sheet,col=c+4,ren=r+5,val="Disp.",color="00FFCC",aline=True,bold=True)
        cellStyle(sheet,col=c+4,ren=r+6,val="Forces",color="00FFCC",aline=True,bold=True)
        for i in range(2):
            cellStyle(sheet,col=c+5+i,ren=r+5,val=self.u_l[i,0],color="9BFFEC",aline=True)
        for i in range(2):
            cellStyle(sheet,col=c+5+i,ren=r+6,val=self.f_l[i,0],color="9BFFEC",aline=True)


class TrussStructure():
    def __init__(self):     # Se crea la estructura reticulada
        self.J = {}     # Se crea un diccionario de los nudos que tiene la estructura
        self.Joints = {}    # Se crea un diccionario con los nudos que son usados en la estructura
        self.Elements = {}  # Se crea un diccionario con los elementos que tiene la estructura
        self.nGdL = 0    # Número de grados de libertad de la estructura
        self.gdl = 0     # Variable auxiliar para asignar los grados de libertad a los nudos
        self.constraints = []
        self.forces = []

    def add_joint(self,x,y,name):
        """Agrega un nudo a la estructura.

        Parametros
        ----------
        x : float
            Coordenada X del nudo.
        y : float
            Coordenada Y del nudo.
        name : str
            Nombre del nudo.
        """
        self.J[name] = Joint(x,y,name)

    def add_element(self,Ji,Jf,section,name):
        """Agrega un elemento biarticulado a la estructura.

        Parametros
        ----------
        Ji : str
            Nombre del nudo inicial del elemento.
        Jf : str
            Nombre del nudo final del elemento.
        section : Section object
            Sección del elemento.
        name : str
            Nombre del elemento.
        """
        if Ji not in self.J:
            print(f"Error al agregar el elemento {name}, el nudo inicial indicado no ha sido definido")
            return 0
        if Jf not in self.J:
            print(f"Error al agregar el elemento {name}, el nudo final indicado no ha sido definido")
            return 0
        if not self.J[Ji].is_used:
            self.Joints[Ji] = self.J[Ji]
            self.Joints[Ji].use([self.gdl,self.gdl+1])
            self.gdl += 2
            self.nGdL += 2
        if not self.J[Jf].is_used:
            self.Joints[Jf] = self.J[Jf]
            self.Joints[Jf].use([self.gdl,self.gdl+1])
            self.gdl += 2
            self.nGdL += 2
        self.Elements[name] = TrussElement(self.Joints[Ji],self.Joints[Jf],section,name)
        self.Elements[name].assignGDL(self.Joints[Ji].GdL+self.Joints[Jf].GdL)

    def add_constraint(self,J,const={"x":0,"y":0}):
        """Agrega restricciones de movimiento a un nudo de la estructura

        Parameters
        ----------
        J : str
            Nombre del nudo que será restringido.
        const : list
            Lista con los número de los grados de libertad restringidos. Siendo 1 dirección "x", 2 dirección "y". Ejemplos: [1],
            [1,2], [2]
        """
        if "x" in const:
            if const["x"] == 1: self.constraints.append(self.Joints[J].GdL[0])
        if "y" in const:
            if const["y"] == 1: self.constraints.append(self.Joints[J].GdL[1])

    def add_nodal_force(self,J,force={"x":0, "y":0}):
        if "x" in force:
            if force["x"] != 0: self.forces.append([self.Joints[J].GdL[0],force["x"]])
        if "y" in force:
            if force["y"] != 0: self.forces.append([self.Joints[J].GdL[1],force["y"]])

    def Analyze(self):
        self.K = zeros((self.nGdL,self.nGdL))
        for e in self.Elements:
            for i in range(4):
                for j in range(4):
                    self.K[self.Elements[e].GdL[i],self.Elements[e].GdL[j]] += self.Elements[e].k_glob[i,j]
        self.F = zeros((self.nGdL,1))
        for g,v in self.forces:
            self.F[g,0] += v
        self.K_r = copy(self.K)
        self.K_r = delete(self.K_r,self.constraints,axis=0)
        self.K_r = delete(self.K_r,self.constraints,axis=1)
        self.F_r = copy(self.F)
        self.F_r = delete(self.F_r,self.constraints,axis=0)
        self.U_r = solve(self.K_r,self.F_r)
        self.U = zeros((self.nGdL,1))
        j = 0
        for i in range(self.nGdL):
            if i not in self.constraints:
                self.U[i] = self.U_r[j]
                j += 1
        for e in self.Elements:
            self.Elements[e].deform(self.U)
    
    def to_excel(self):
        wb = Workbook()
        sh1 = wb.create_sheet("Truss",0)
        cellStyle(sh1,col=2,ren=2,val="GENERAL",mergeCell=8,color="FFFF00",aline=True,bold=True)
        cellStyle(sh1,col=2,ren=3,val="Elements:",mergeCell=6,color="00FFCC",aline=False,bold=True)
        cellStyle(sh1,col=7,ren=3,val=len(self.Elements),mergeCell=8,color="9BFFEC",aline=True)
        cellStyle(sh1,col=2,ren=4,val="Joints:",mergeCell=6,color="00FFCC",aline=False,bold=True)
        cellStyle(sh1,col=7,ren=4,val=len(self.Joints),mergeCell=8,color="9BFFEC",aline=True)
        cellStyle(sh1,col=2,ren=5,val="Degrees of Freedom:",mergeCell=6,color="00FFCC",aline=False,bold=True)
        cellStyle(sh1,col=7,ren=5,val=2*len(self.Joints),mergeCell=8,color="9BFFEC",aline=True)
        cellStyle(sh1,col=2,ren=6,val="Reactions:",mergeCell=6,color="00FFCC",aline=False,bold=True)
        cellStyle(sh1,col=7,ren=6,val=len(self.constraints),mergeCell=8,color="9BFFEC",aline=True)
        j = 9
        for elem in self.Elements:
            self.Elements[elem].elemento_excel(sh1,2,j)
            j += 22
        n = int(2*len(self.Joints))
        for i in range(n):
            for j in range(n):
                color = "9BFFEC" if i in self.constraints or j in self.constraints else "00FFCC"
                bold = False if i in self.constraints or j in self.constraints else True
                cellStyle(sh1,col=10+j,ren=4+i,val=self.K[i,j],color=color,aline=True,bold=bold)
            cellStyle(sh1,col=11+n,ren=4+i,val=self.U[i,0],color=color,aline=True,bold=bold)
            cellStyle(sh1,col=13+n,ren=4+i,val=self.F[i,0],color=color,aline=True,bold=bold)
        return wb

