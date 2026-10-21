import math
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Motor System Lab", page_icon="⚙️", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:1rem;max-width:1600px}
.lab-sub{color:#64748b;margin-top:-.7rem}
div[data-testid="stMetric"]{border:1px solid #d8e1ea;padding:12px;border-radius:10px;background:rgba(120,140,160,.05)}
section[data-testid="stSidebar"]{border-right:1px solid #d8e1ea}
</style>""", unsafe_allow_html=True)


def render_mechanical_motion(motor_name, rpm, ratio, degradation, status):
    """Browser-side SVG/CSS animation; speed/wobble mapping is an illustrative wear visualization."""
    safe_name = motor_name.replace("<", "").replace(">", "")
    # A phenomenological display mapping: increasing degradation reduces displayed output speed
    # and increases visible output wobble. This is not a calibrated gearbox wear law.
    output_rpm = max(0.0, rpm / max(ratio, 1) * (1.0 - 0.70 * degradation))
    motor_period = max(0.18, 60.0 / max(abs(rpm), 1.0))
    input_gear_period = motor_period
    output_period = max(0.25, 60.0 / max(abs(output_rpm), 1.0))
    wobble = 0.0 if degradation <= 0 else min(5.0, 0.5 + degradation * 8.0)
    state = "STALL / OVERLOAD" if status == "STALL / OVERLOAD" else ("DEGRADED" if degradation > 0 else "NORMAL")
    html = f"""
    <!doctype html><html><head><meta charset="utf-8">
    <style>
      * {{ box-sizing:border-box; }}
      body {{ margin:0; font-family:Arial,sans-serif; background:transparent; color:#e5edf5; }}
      .frame {{ border:1px solid #31465c; border-radius:14px; padding:12px; background:linear-gradient(135deg,#101f30,#172b40); }}
      .head {{ display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:6px; }}
      .head strong {{ font-size:15px; letter-spacing:.02em; }}
      .pill {{ border-radius:999px; padding:4px 8px; font-size:10px; font-weight:700; background:#164e63; color:#a5f3fc; }}
      .pill.bad {{ background:#7f1d1d; color:#fecaca; }} .pill.warn {{ background:#78350f; color:#fde68a; }}
      svg {{ width:100%; height:auto; display:block; }}
      .label {{ fill:#cbd5e1; font-size:11px; }} .small {{ fill:#94a3b8; font-size:9px; }}
      .shaft {{ stroke:#9fb3c8; stroke-width:5; stroke-linecap:round; }}
      .gear {{ transform-box:fill-box; transform-origin:center; }}
      .rotor {{ transform-box:fill-box; transform-origin:center; }}
      .motorSpin {{ animation: spin {motor_period:.3f}s linear infinite; }}
      .inputSpin {{ animation: spin {input_gear_period:.3f}s linear infinite; }}
      .outputSpin {{ animation: spinReverse {output_period:.3f}s linear infinite; }}
      .drumSpin {{ animation: spinReverse {output_period:.3f}s linear infinite; }}
      .wobble {{ animation: wobble {max(0.22, output_period/2):.3f}s ease-in-out infinite; }}
      @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
      @keyframes spinReverse {{ to {{ transform:rotate(-360deg); }} }}
      @keyframes wobble {{ 0%,100% {{ transform:translateX(0) rotate(0deg); }} 50% {{ transform:translateX({wobble:.2f}px) rotate({wobble/2:.2f}deg); }} }}
      .stopped {{ animation-play-state:paused !important; }}
      .legend {{ display:flex; gap:12px; flex-wrap:wrap; color:#a9bacb; font-size:10px; padding:2px 3px 0; }}
      .dot {{ display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:4px; }}
      .readout {{ display:flex; gap:8px; margin-top:8px; }}
      .readout div {{ flex:1; padding:7px 9px; background:#0b1725; border:1px solid #293d52; border-radius:8px; }}
      .readout span {{ display:block; color:#94a3b8; font-size:10px; }}
      .readout b {{ font-size:13px; }}
    </style></head><body>
    <div class="frame">
      <div class="head"><strong>MECHANICAL MOTION · {safe_name}</strong>
      <span class="pill {'bad' if state=='STALL / OVERLOAD' else ('warn' if state=='DEGRADED' else '')}">{state}</span></div>
      <svg viewBox="0 0 620 250" role="img" aria-label="Animated motor, gears and output drum">
        <defs>
          <linearGradient id="motorBody" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3b82a0"/><stop offset="1" stop-color="#1e4562"/></linearGradient>
          <radialGradient id="gearFill"><stop offset="0" stop-color="#64748b"/><stop offset="1" stop-color="#334155"/></radialGradient>
        </defs>
        <!-- Motor casing -->
        <rect x="18" y="66" width="130" height="94" rx="13" fill="url(#motorBody)" stroke="#6ea9c4" stroke-width="2"/>
        <rect x="32" y="80" width="102" height="66" rx="7" fill="#10263a" stroke="#5b829a"/>
        <g class="rotor motorSpin {'stopped' if rpm < 1 else ''}" transform="translate(83 113)">
          <circle r="25" fill="#1e293b" stroke="#93c5fd" stroke-width="3"/>
          <circle r="6" fill="#dbeafe"/>
          <path d="M0 -21 L5 -7 L21 0 L7 5 L0 21 L-5 7 L-21 0 L-7 -5 Z" fill="#60a5fa" stroke="#bfdbfe" stroke-width="1.2"/>
        </g>
        <line x1="148" y1="113" x2="210" y2="113" class="shaft"/>
        <!-- Input gear -->
        <g class="gear inputSpin {'stopped' if rpm < 1 else ''}" transform="translate(239 113)">
          <circle r="37" fill="url(#gearFill)" stroke="#a8b6c7" stroke-width="3" stroke-dasharray="7 4"/>
          <circle r="25" fill="#24364b" stroke="#94a3b8" stroke-width="2"/>
          <g stroke="#cbd5e1" stroke-width="3" stroke-linecap="round">
            <line x1="0" y1="-21" x2="0" y2="-7"/><line x1="21" y1="0" x2="7" y2="0"/>
            <line x1="0" y1="21" x2="0" y2="7"/><line x1="-21" y1="0" x2="-7" y2="0"/>
            <line x1="-15" y1="-15" x2="-6" y2="-6"/><line x1="15" y1="-15" x2="6" y2="-6"/>
            <line x1="15" y1="15" x2="6" y2="6"/><line x1="-15" y1="15" x2="-6" y2="6"/>
          </g><circle r="5" fill="#e2e8f0"/>
        </g>
        <!-- Output gear, visibly slower as degradation rises -->
        <g class="gear outputSpin {'stopped' if output_rpm < 1 else ''} wobble" transform="translate(337 113)">
          <circle r="49" fill="url(#gearFill)" stroke="#fbbf24" stroke-width="3" stroke-dasharray="9 4"/>
          <circle r="34" fill="#24364b" stroke="#cbd5e1" stroke-width="2"/>
          <g stroke="#f8fafc" stroke-width="4" stroke-linecap="round">
            <line x1="0" y1="-30" x2="0" y2="-9"/><line x1="30" y1="0" x2="9" y2="0"/>
            <line x1="0" y1="30" x2="0" y2="9"/><line x1="-30" y1="0" x2="-9" y2="0"/>
            <line x1="-21" y1="-21" x2="-7" y2="-7"/><line x1="21" y1="-21" x2="7" y2="-7"/>
            <line x1="21" y1="21" x2="7" y2="7"/><line x1="-21" y1="21" x2="-7" y2="7"/>
          </g><circle r="7" fill="#fbbf24"/>
        </g>
        <line x1="386" y1="113" x2="452" y2="113" class="shaft"/>
        <!-- Output drum -->
        <g class="drumSpin {'stopped' if output_rpm < 1 else ''}" transform="translate(485 113)">
          <ellipse cx="0" cy="-27" rx="25" ry="10" fill="#0f766e" stroke="#5eead4" stroke-width="2"/>
          <rect x="-25" y="-27" width="50" height="54" fill="#115e59" stroke="#5eead4" stroke-width="2"/>
          <ellipse cx="0" cy="27" rx="25" ry="10" fill="#134e4a" stroke="#5eead4" stroke-width="2"/>
          <path d="M-15 -22 L-15 22 M0 -22 L0 22 M15 -22 L15 22" stroke="#99f6e4" stroke-width="2"/>
        </g>
        <path d="M485 151 L485 183 Q485 194 497 194 L511 194" stroke="#fbbf24" stroke-width="3" fill="none"/>
        <rect x="493" y="190" width="35" height="28" rx="4" fill="#a16207" stroke="#fcd34d" stroke-width="2"/>
        <text x="83" y="48" text-anchor="middle" class="label">DC MOTOR</text>
        <text x="239" y="53" text-anchor="middle" class="label">INPUT GEAR</text>
        <text x="337" y="45" text-anchor="middle" class="label">OUTPUT GEAR</text>
        <text x="485" y="53" text-anchor="middle" class="label">LOAD DRUM</text>
        <text x="278" y="202" text-anchor="middle" class="small">Gear reduction {ratio}:1</text>
        <text x="278" y="218" text-anchor="middle" class="small">Degradation {degradation*100:.0f}%</text>
        <text x="565" y="208" text-anchor="middle" class="small">LOAD</text>
      </svg>
      <div class="legend">
        <span><i class="dot" style="background:#60a5fa"></i>Motor rotation</span>
        <span><i class="dot" style="background:#fbbf24"></i>Gear transmission</span>
        <span><i class="dot" style="background:#5eead4"></i>Output motion</span>
      </div>
      <div class="readout">
        <div><span>Motor speed</span><b>{rpm:.1f} RPM</b></div>
        <div><span>Displayed output speed</span><b>{output_rpm:.1f} RPM</b></div>
        <div><span>Visible wobble index</span><b>{degradation*100:.0f}%</b></div>
      </div>
    </div>
    </body></html>
    """
    components.html(html, height=390, scrolling=False)


st.title("⚙️ Motor System Lab")
st.markdown('<p class="lab-sub">MATLAB-inspired interactive motor and gearbox simulation · M1 / M2 / M3</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("SYSTEM PARAMETERS")
    voltage = st.slider("Supply voltage (V)", 0.0, 48.0, 24.0, 0.5)
    ratio = st.select_slider("Gear reduction", [1,2,3,4,5,6,8,10,12,16], value=4, format_func=lambda x:f"{x}:1")
    gear_eff = st.slider("Gearbox efficiency (%)", 50, 99, 90, 1)/100
    st.divider()
    st.header("LOAD")
    mass = st.slider("Equivalent lifted mass (kg)", 0.0, 20.0, 2.0, 0.1)
    radius = st.slider("Drum radius (m)", 0.01, 0.20, 0.05, 0.005)
    gravity = st.number_input("Gravity (m/s²)", 9.0, 10.0, 9.81, 0.01)
    st.divider()
    st.header("FAULT INJECTION")
    degradation = st.slider("Mechanical degradation (%)", 0, 90, 0, 5)/100
    force_stall = st.selectbox("Force stall on motor", ["None","M1","M2","M3"])
    duration = st.slider("Plot duration (s)", 2, 30, 10)

load_torque = mass*gravity*radius
eff = gear_eff*(1-degradation)
motor_defaults = {
    "M1": {"label":"Drive motor","R":2.0,"Kt":0.08,"Ke":0.08,"Ilim":8.0},
    "M2": {"label":"Intermediate motor","R":1.6,"Kt":0.07,"Ke":0.07,"Ilim":7.0},
    "M3": {"label":"Output motor","R":2.4,"Kt":0.09,"Ke":0.09,"Ilim":6.0}
}
tabs = st.tabs(["M1 · Drive","M2 · Intermediate","M3 · Output","System analysis","Model & export"])
specs, results = {}, {}

def calculate(name, s):
    req_t = load_torque/max(ratio*eff,1e-9)
    req_i = req_t/max(s["Kt"],1e-9)
    current = min(req_i,s["Ilim"])
    omega = max(0,(voltage-current*s["R"])/max(s["Ke"],1e-9))
    stalled = (force_stall==name) or req_i>s["Ilim"] or voltage<=current*s["R"]
    if force_stall==name:
        current=min(voltage/max(s["R"],1e-9),s["Ilim"])
        omega=0
    elif stalled: omega=0
    torque=s["Kt"]*current
    rpm=omega*60/(2*math.pi)
    out_rpm=rpm/ratio
    out_torque=torque*ratio*eff
    pin=voltage*current
    pout=out_torque*omega/ratio
    status="STALL / OVERLOAD" if stalled else ("DEGRADED" if degradation else "OPERATING")
    return dict(name=name,spec=s,req_t=req_t,req_i=req_i,current=current,omega=omega,rpm=rpm,
                out_rpm=out_rpm,torque=torque,out_torque=out_torque,pin=pin,
                pm=torque*omega,pout=pout,eta=min(100,max(0,pout/pin*100 if pin else 0)),
                stalled=stalled,status=status)

for i,name in enumerate(["M1","M2","M3"]):
    with tabs[i]:
        st.subheader(f"{name} — {motor_defaults[name]['label']}")
        st.caption("Each motor has independent electrical parameters. All motors are shown together in System analysis.")
        c=st.columns(4)
        d=motor_defaults[name]
        with c[0]: R=st.number_input("Resistance (Ω)",0.1,20.0,d["R"],0.1,key=f"{name}R")
        with c[1]: Kt=st.number_input("Torque constant Kt",0.005,1.0,d["Kt"],0.005,format="%.3f",key=f"{name}Kt")
        with c[2]: Ke=st.number_input("Back-EMF constant Ke",0.005,1.0,d["Ke"],0.005,format="%.3f",key=f"{name}Ke")
        with c[3]: Ilim=st.number_input("Current limit (A)",0.5,30.0,d["Ilim"],0.5,key=f"{name}I")
        specs[name]={"R":R,"Kt":Kt,"Ke":Ke,"Ilim":Ilim}
        r=calculate(name,specs[name]); results[name]=r
        if r["stalled"]: st.error("STALL / OVERLOAD — review load, voltage, current limit and motor constants.")
        elif degradation: st.warning("Mechanical degradation is enabled; transmission efficiency is reduced.")
        else: st.success("Operating point calculated from the current model.")
        m=st.columns(5)
        for col,label,value in zip(m,["Motor speed","Output speed","Motor torque","Current","Output torque"],
            [f'{r["rpm"]:,.0f} RPM',f'{r["out_rpm"]:,.1f} RPM',f'{r["torque"]:.3f} N·m',f'{r["current"]:.2f} A',f'{r["out_torque"]:.3f} N·m']):
            col.metric(label,value)
        fig=go.Figure()
        blocks=[(.03,.29,.29,.73,"MOTOR",f'{r["rpm"]:.0f} RPM<br>{r["current"]:.2f} A',"#dbeafe","#1d4ed8"),
                (.365,.29,.635,.73,"GEARBOX",f'{ratio}:1<br>η {eff*100:.0f}%',"#fef3c7","#a16207"),
                (.71,.29,.97,.73,"LOAD",f'{r["out_rpm"]:.1f} RPM<br>{r["out_torque"]:.2f} N·m',"#dcfce7","#15803d")]
        for x0,y0,x1,y1,title,body,fill,line in blocks:
            fig.add_shape(type="rect",x0=x0,y0=y0,x1=x1,y1=y1,line=dict(color=line,width=2),fillcolor=fill)
            fig.add_annotation(x=(x0+x1)/2,y=.59,text=f"<b>{title}</b>",showarrow=False,font=dict(size=15,color="#10243a"))
            fig.add_annotation(x=(x0+x1)/2,y=.43,text=body,showarrow=False,font=dict(size=12,color="#10243a"))
        fig.add_annotation(x=.33,y=.5,text="➜",showarrow=False,font=dict(size=24,color="#64748b"))
        fig.add_annotation(x=.67,y=.5,text="➜",showarrow=False,font=dict(size=24,color="#64748b"))
        fig.update_layout(height=245,margin=dict(l=5,r=5,t=5,b=5),xaxis=dict(visible=False,range=[0,1]),yaxis=dict(visible=False,range=[0,1]),plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True)
        st.markdown("##### Animated mechanical transmission")
        render_mechanical_motion(name, r["rpm"], ratio, degradation, r["status"])
        p=st.columns(4)
        for col,label,value in zip(p,["Electrical input","Motor shaft power","Output power","Estimated efficiency"],
            [f'{r["pin"]:.1f} W',f'{r["pm"]:.1f} W',f'{r["pout"]:.1f} W',f'{r["eta"]:.1f}%']):
            col.metric(label,value)
        st.caption(f'Required motor torque for shared load: {r["req_t"]:.3f} N·m · Unrestricted current estimate: {r["req_i"]:.2f} A')

for name in ["M1","M2","M3"]:
    if name not in results:
        results[name]=calculate(name,motor_defaults[name].copy())
        specs[name]=motor_defaults[name].copy()

with tabs[3]:
    st.subheader("All motors — system dashboard")
    cards=st.columns(3)
    for col,name in zip(cards,["M1","M2","M3"]):
        r=results[name]
        with col:
            st.markdown(f"#### {name} · {motor_defaults[name]['label']}")
            st.caption(f"Status: **{r['status']}**")
            st.metric("Motor speed",f'{r["rpm"]:.0f} RPM')
            st.metric("Motor torque",f'{r["torque"]:.3f} N·m')
            st.metric("Current",f'{r["current"]:.2f} A')
    df=pd.DataFrame([{"Motor":n,"Status":results[n]["status"],"Motor RPM":results[n]["rpm"],"Output RPM":results[n]["out_rpm"],"Current (A)":results[n]["current"],"Motor torque (N·m)":results[n]["torque"],"Output torque (N·m)":results[n]["out_torque"],"Input power (W)":results[n]["pin"],"Output power (W)":results[n]["pout"],"Efficiency (%)":results[n]["eta"]} for n in ["M1","M2","M3"]])
    st.dataframe(df,hide_index=True,use_container_width=True)
    chart=go.Figure()
    for col in ["Motor RPM","Output RPM"]: chart.add_trace(go.Bar(name=col,x=df["Motor"],y=df[col]))
    chart.update_layout(barmode="group",height=330,yaxis_title="RPM",margin=dict(l=5,r=5,t=15,b=5),legend=dict(orientation="h",y=1.12))
    st.plotly_chart(chart,use_container_width=True)
    st.subheader("Mechanical motion — all three motors")
    motion_cols = st.columns(3)
    for col, name in zip(motion_cols, ["M1", "M2", "M3"]):
        with col:
            render_mechanical_motion(name, results[name]["rpm"], ratio, degradation, results[name]["status"])
    st.subheader("Speed and current response")
    t=np.linspace(0,duration,240)
    fig=make_subplots(specs=[[{"secondary_y":True}]])
    for n,tau in [("M1",.45),("M2",.60),("M3",.75)]:
        r=results[n]; speed=r["rpm"]*(1-np.exp(-t/tau))
        if r["stalled"]: speed=np.zeros_like(t)
        current=r["current"]*(.75*np.exp(-t/.2)+.25)
        fig.add_trace(go.Scatter(x=t,y=speed,name=f"{n} speed (RPM)"),secondary_y=False)
        fig.add_trace(go.Scatter(x=t,y=current,name=f"{n} current (A)",line=dict(dash="dot")),secondary_y=True)
    fig.update_xaxes(title_text="Time (s)"); fig.update_yaxes(title_text="Speed (RPM)",secondary_y=False); fig.update_yaxes(title_text="Current (A)",secondary_y=True)
    fig.update_layout(height=380,margin=dict(l=5,r=5,t=15,b=5),legend=dict(orientation="h",y=1.18))
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Transient curves use illustrative time constants and are not validated dynamic motor responses.")

with tabs[4]:
    st.subheader("Model equations")
    st.latex(r"T_L=mgr")
    st.latex(r"T_m=\frac{T_L}{N\eta_{eff}},\\qquad \eta_{eff}=\eta(1-d)")
    st.latex(r"T=K_t I,\\qquad V=K_e\omega+IR")
    st.latex(r"RPM=\omega\frac{60}{2\pi},\\qquad RPM_{out}=RPM_m/N")
    st.latex(r"P_{in}=VI,\\qquad P_{out}=T_{out}\omega_{out}")
    st.warning("Educational steady-state model only. Default motor constants are illustrative. Use datasheet values and validate against measured hardware before making engineering or safety decisions.")
    df=pd.DataFrame([{"Motor":n,"Voltage (V)":voltage,"Resistance (Ω)":results[n]["spec"]["R"],"Kt":results[n]["spec"]["Kt"],"Ke":results[n]["spec"]["Ke"],"Current limit (A)":results[n]["spec"]["Ilim"],"Gear ratio":ratio,"Efficiency used (%)":eff*100,"Load (kg)":mass,"Drum radius (m)":radius,"Load torque (N·m)":load_torque,"Motor RPM":results[n]["rpm"],"Output RPM":results[n]["out_rpm"],"Current (A)":results[n]["current"],"Motor torque (N·m)":results[n]["torque"],"Output torque (N·m)":results[n]["out_torque"],"Input power (W)":results[n]["pin"],"Output power (W)":results[n]["pout"],"Status":results[n]["status"]} for n in ["M1","M2","M3"]])
    st.download_button("Download all motor results (CSV)",df.to_csv(index=False).encode("utf-8"),"motor_system_results.csv","text/csv",type="primary")
    st.dataframe(df,hide_index=True,use_container_width=True)

st.divider()
st.caption("Motor System Lab · Python interactive simulation · Calculated estimates, not live sensor readings.")
