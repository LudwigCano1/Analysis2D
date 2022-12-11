import streamlit as st
import plotly_express as px
from io import BytesIO
from tempfile import NamedTemporaryFile
from Gadest import TrussStructure,Section

st.set_page_config(layout="wide")

Armadura = TrussStructure()

dict_Sections = {}
dict_N = {}
dict_Nudos = {}
dict_Elem = {}

with st.sidebar:
    T1,T2,T3,T4,T5 = st.tabs(["[ General ]","[ Section Properties ]","[ Draw Geometry ]","[ Assign ]","[ Analyze ]"])
    st.write("---")

G1,G2 = st.tabs(["[ Undeformed ]","[ Deformed ]"])

with T1: #GENERAL
    #st.title("Truss Analysis")
    #st.write("**This app analyzes truss structures using the stiffness method.**")
    #st.write("Temperature changes are not considered.")
    #st.write("Fabrication error of elements are not considered.")
    #st.markdown("[aea](https://www.google.com)")
    with st.expander("Units:",expanded=True):
        c1,c2 = st.columns(2)
        with c1:
            st.write("Length units:")
            length_unit = st.text_input("LU","m",label_visibility="collapsed")
        with c2:
            st.write("Force units:")
            force_unit = st.text_input("FU","kN",label_visibility="collapsed")
    with st.expander("Colors:",expanded=True):
        c1,c2 = st.columns([3,1])
        with c1: st.write("Node color:")
        with c2: col_joint = st.color_picker("col_j","#FD0606",label_visibility="collapsed")
        c1,c2 = st.columns([3,1])
        with c1: st.write("Element color:")
        with c2: col_elem = st.color_picker("col_e","#07F7C0",label_visibility="collapsed")
        c1,c2 = st.columns([3,1])
        with c1: st.write("Constraint color:")
        with c2: col_const = st.color_picker("col_c","#1200FF",label_visibility="collapsed")
        c1,c2 = st.columns([3,1])
        with c1: st.write("Force color:")
        with c2: col_forces = st.color_picker("col_c","#E000FF",label_visibility="collapsed")

with T2: #SECTION PROPERTIES
    st.write("Number of sections:")
    nSections = st.number_input("nSections",1,20,1,1,label_visibility="collapsed")
    c1,c2,c3 = st.columns([1.5,2,2],gap="medium")
    lab_A = f"A ({length_unit}²):"
    lab_E = f"E ({force_unit}/{length_unit}²)"
    lab_n = "Label:"
    with c1: st.write("**Label:**")
    with c2: st.write("**"+lab_E+"**")
    with c3: st.write("**"+lab_A+"**")
    for i in range(nSections):
        c1,c2,c3 = st.columns([1.5,2,2])
        with c1: S_label = str(i+1).zfill(2)+"-"+st.text_input(lab_n,label_visibility="collapsed",value="section")
        with c2: S_elas = st.number_input(lab_E,value=1.0,label_visibility="collapsed")
        with c3: S_area = st.number_input(lab_A,value=1.0,label_visibility="collapsed")
        dict_Sections[S_label] = Section(S_label,S_elas,S_area)
        lab_n += " "
        lab_A += " "
        lab_E += " "


with T3: #DRAW GEOMETRY
    T3_1,T3_2 = st.tabs(["[ Joints ]","[ Elements ]"])
    with T3_1: #JOINTS
        st.write("Number of joints:")
        nNudos = st.number_input("nNudos",2,100,2,1,label_visibility="collapsed")
        plot1 = px.line(x=[0],y=[0],labels={"x":f"x ({length_unit})","y":f"y ({length_unit})"},height=600)
        labX = f"Coord X ({length_unit}):"
        labY = f"Coord Y ({length_unit}):"
        c1,c2,c3 = st.columns([1,2,2],gap="medium")
        with c1: st.write("**Joint**")
        with c2: st.write("**"+labX+"**")
        with c3: st.write("**"+labY+"**")
        for i in range(nNudos):
            label = "J"+str(i+1).zfill(2)
            c1,c2,c3 = st.columns([1,2,2],gap="medium")
            with c1:
                st.write(" ")
                st.write("**"+label+"**")
            with c2:
                coord_x = st.number_input(labX,label_visibility="collapsed")
            with c3:
                coord_y = st.number_input(labY,label_visibility="collapsed")
            Armadura.add_joint(coord_x,coord_y,label)
            plot1.update_layout(showlegend=False)
            #plot1.add_scatter(x=[coord_x],y=[coord_y],mode="markers+text",marker={"color":col_joint,"size":15},name=label,text=label,textposition="bottom center")
            labX += " "
            labY += " "
        
    with T3_2: #ELEMENTS
        c1,c2 = st.columns([1,1])
        with c1: st.write("Number of elements:")
        with c2: nElements = st.number_input("nElements",1,100,1,1,label_visibility="collapsed")
        lab_i = "From:"
        lab_f = "To:"
        lab_S = "Section:"
        c1,c2,c3,c4 = st.columns([1.2,2,2,2])
        with c1: st.write("**Elements**")
        with c2: st.write("**"+lab_i+"**")
        with c3: st.write("**"+lab_f+"**")
        with c4: st.write("**"+lab_S+"**")
        #plot1.data = []
        for i in range(nElements):
            label = "T"+str(i+1).zfill(2)
            c1,c2,c3,c4 = st.columns([1.2,2,2,2])
            with c1:
                st.write(" ")
                st.write("**"+label+"**")
            with c2:
                Joint_i = st.selectbox(lab_i,options=list(Armadura.J.keys()),label_visibility="collapsed")
            with c3:
                copiaListaNudos = list(Armadura.J.keys())[:]
                copiaListaNudos.remove(Joint_i)
                Joint_f = st.selectbox(lab_f,options=copiaListaNudos,label_visibility="collapsed")
            with c4:
                Sect = st.selectbox(lab_S,options=dict_Sections,label_visibility="collapsed")
            Armadura.add_element(Joint_i,Joint_f,dict_Sections[Sect],label)
            #plot1.add_scatter(x=[dict_N[Joint_i].X,dict_N[Joint_f].X],y=[dict_N[Joint_i].Y,dict_N[Joint_f].Y],mode="lines",line={"color":col_elem,"width":4},name=label)
            #plot1.add_scatter(x=[0.5*(dict_N[Joint_i].X+dict_N[Joint_f].X)],y=[0.5*(dict_N[Joint_i].Y+dict_N[Joint_f].Y)],mode="lines+text",line={"color":col_elem,"width":4},name=label,text=label,textposition="bottom center")
            lab_i += " "
            lab_f += " "
            lab_S += " "
        GdL = 0
        for i in dict_Nudos:
            dict_Nudos[i].use(GdL,GdL+1,GdL+2)
            GdL += 3
            #plot1.add_scatter(x=[dict_Nudos[i].X],y=[dict_Nudos[i].Y],mode="markers",marker={"color":col_joint,"size":15},name=i)

x_max = Armadura.Joints["J01"].x
x_min = Armadura.Joints["J01"].x
y_max = Armadura.Joints["J01"].y
y_min = Armadura.Joints["J01"].y
for nudo in Armadura.Joints:
    if Armadura.Joints[nudo].x < x_min:
        x_min = Armadura.Joints[nudo].x
    if Armadura.Joints[nudo].x > x_max:
        x_max = Armadura.Joints[nudo].x
    if Armadura.Joints[nudo].y < y_min:
        y_min = Armadura.Joints[nudo].y
    if Armadura.Joints[nudo].y > y_max:
        y_max = Armadura.Joints[nudo].y
dist_max = max(x_max-x_min,y_max-y_min)/5

with T4: #ASSIGN
    T4_1,T4_2 = st.tabs(["[ Constraints ]","[ Loads ]"])
    with T4_1:
        st.write("Active the checkbox to restraint the displacement in that direction")
        c1,c2,c3,c4,c5 = st.columns([2,1,1,1,2])
        label = " "
        with c2: st.write("**Joint**")
        with c3: st.write("**RX**")
        with c4: st.write("**RY**")
        const = []
        for i in Armadura.Joints:
            c1,c2,c3,c4,c5 = st.columns([2,1,1,1,2])
            with c2: st.write(i)
            with c3: DX = st.checkbox(label=label)
            label += " "
            with c4: DY = st.checkbox(label=label)
            label += " "
            Armadura.add_constraint(i,{"x":int(DX),"y":int(DY)})
            # if DX:
            #     const.append(Armadura.Joints[i].gdl[0])
            #     plot1.add_scatter(x=[dict_Nudos[i].X],y=[dict_Nudos[i].Y],marker={"symbol":"48","size":20,"color":col_const})
            # if DY:
            #     const.append(Armadura.Joints[i].gdl[1])
            #     plot1.add_scatter(x=[dict_Nudos[i].X],y=[dict_Nudos[i].Y],marker={"symbol":"45","size":20,"color":col_const})

    with T4_2:
        c1,c2 = st.columns(2)
        with c1: st.write("**Number of Nodal Loads:**")
        with c2: nForces = st.number_input("nForces",1,100,1,1,label_visibility="collapsed")
        labJForces = " "
        labDForces = " "
        labVForces = " "
        list_forces = []
        c2,c3,c4,c5 = st.columns([2,2,2,1])
        with c2: st.write("**Joint**")
        with c3: st.write("**Direction**")
        with c4: st.write("**Magnitud**")
        for i in range(nForces):
            c2,c3,c4,c5 = st.columns([2,2,2,1])
            with c2:
                ""
                J = st.selectbox(label=labJForces,options=Armadura.Joints,label_visibility="collapsed")
            with c3: D = st.radio(label=labDForces,options=("DX","DY"),label_visibility="collapsed")
            with c4:
                ""
                V = st.number_input(label=labVForces,label_visibility="collapsed")
            with c5:
                ""
                st.write(f"{force_unit}")
            labJForces += " "
            labDForces += " "
            labVForces += " "
            if D == "DX":
                Armadura.add_nodal_force(J,{"x":V})
                
                #list_forces.append([dict_Nudos[J].gdl[0],V])
                triang = "48" if V >= 0 else "47"
                posit = "top left" if V >=0 else "top right"
                #if V != 0: plot1.add_scatter(x=[dict_Nudos[J].X],y=[dict_Nudos[J].Y],mode="markers+text",marker={"symbol":triang,"size":20,"color":col_forces},text=str(abs(V))+" "+force_unit,textposition=posit,textfont={"size":18,"color":col_forces})
                factor = -0.8 if V >= 0 else 0.8
                #if V != 0: plot1.add_scatter(x=[dict_N[J].X + factor * dist_max,dict_N[J].X],y=[dict_N[J].Y,dict_N[J].Y],mode="lines",line={"color":col_forces,"width":4},name=label)
            elif D == "DY":
                Armadura.add_nodal_force(J,{"y":V})

                #list_forces.append([dict_Nudos[J].gdl[1],V])
                triang = "45" if V >= 0 else "46"
                posit = "bottom right" if V >=0 else "top right"
                #if V != 0: plot1.add_scatter(x=[dict_Nudos[J].X],y=[dict_Nudos[J].Y],mode="markers+text",marker={"symbol":triang,"size":20,"color":col_forces},text=str(abs(V))+" "+force_unit,textposition=posit,textfont={"size":18,"color":col_forces})
                factor = -0.8 if V >= 0 else 0.8
                #if V != 0: plot1.add_scatter(x=[dict_N[J].X,dict_N[J].X],y=[dict_N[J].Y+factor*dist_max,dict_N[J].Y],mode="lines",line={"color":col_forces,"width":4},name=label)

with G1:
    st.plotly_chart(plot1,use_container_width=True)

with T5: # Analysis
    if st.checkbox("Analyze"):
        Armadura.Analyze()
        wb = Armadura.to_excel()

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            data = BytesIO(tmp.read())

        st.download_button("Download Excel",data=data,mime="xlsx",file_name="TrussStructure.xlsx")
