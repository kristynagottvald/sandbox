#!/usr/bin/env python3
"""Generates the simplified, abstract tile art in skills-library/art/*.svg.
Flat outlined boxes, hatched picture areas and simple lines in a few colours, one calm loop each."""
import os
OUT=os.path.join(os.path.dirname(__file__),'..','skills-library','art')
BG='#13151f'; L='#ece8dc'; DIM='#4a4e63'
CO='#ff6b4a'; LI='#c9f25a'; BL='#6a92ff'; YE='#ffd24a'; PK='#ff9ad0'
D=8  # loop seconds

def wrap(body):
    pats=''.join('<pattern id="h%s" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="12" stroke="%s" stroke-width="3"/></pattern>'%(c[1:],c) for c in (CO,LI,BL,YE,PK,L,DIM))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" width="960" height="540"><defs>%s</defs>'
            '<rect width="960" height="540" fill="%s"/>%s</svg>')%(pats,BG,body)

def R(x,y,w,h,r=16,fill='none',s=L,sw=4,extra=''):
    return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" stroke-width="%g" %s/>'%(x,y,w,h,r,fill,s,sw,extra)
def H(x,y,w,h,c=BL,r=12,s=None):
    return (('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="url(#h%s)"/>'%(x,y,w,h,r,c[1:]))+R(x,y,w,h,r,'none',s or c,4))
def F(x,y,w,h,c,r=12): return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s"/>'%(x,y,w,h,r,c)
def T(x,y,w,c=L,h=10): return F(x,y,w,h,c,h/2)
def C(x,y,r,fill='none',s=L,sw=4): return '<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="%g"/>'%(x,y,r,fill,s,sw)
def P(d,fill='none',s=L,sw=4,extra=''): return '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linecap="round" stroke-linejoin="round" %s/>'%(d,fill,s,sw,extra)
def G(inner,extra=''): return '<g %s>%s</g>'%(extra,inner)
def an(attr,vals,dur=D,kt=None,typ=None,begin=0):
    v=';'.join(str(x) for x in vals)
    k=kt or ';'.join('%.3f'%(i/(len(vals)-1)) for i in range(len(vals)))
    t=' type="%s"'%typ if typ else ''
    return '<animate%s attributeName="%s" dur="%ss" begin="%ss" repeatCount="indefinite" keyTimes="%s" values="%s" calcMode="spline" keySplines="%s"%s/>'%('Transform' if typ else '',attr,dur,begin,k,v,';'.join(['.45 0 .25 1']*(len(vals)-1)),t)
def mv(inner,pts,dur=D,begin=0):  # translate through points, ending where it began
    vals=['%g %g'%p for p in pts]
    return '<g>'+inner+an('transform',vals,dur,None,'translate',begin).replace('<animate ','<animateTransform ',1)+'</g>'
def fade(inner,vals,dur=D,begin=0):
    return '<g>'+inner+an('opacity',vals,dur,None,None,begin)+'</g>'
def cursor(x,y):
    return P('M%g %g l0 34 l9 -8 l7 16 l8 -4 l-7 -16 l12 0z'%(x,y),L,BG,3)
def window(x,y,w,h,c=L):
    return R(x,y,w,h,22,'none',c,4)+P('M%g %g H%g'%(x,y+46,x+w),'none',c,4)+C(x+26,y+23,6,c,c,0)+C(x+46,y+23,6,c,c,0)+C(x+66,y+23,6,c,c,0)

T_={}
# 1 brand guidelines site
def t1():
    s=window(120,70,720,400)
    s+=R(150,134,150,306,12,'none',DIM,3)
    for i in range(5): s+=T(168,160+i*54,92,DIM)
    s+=mv(R(158,148,134,38,10,'none',CO,4),[(0,0),(0,0),(0,54),(0,108),(0,162),(0,216),(0,0)],D)
    s+=H(330,134,490,150,BL)+fade(H(330,134,490,150,CO),[0,0,1,1,0,0],D)
    for i,c in enumerate((CO,LI,BL,YE)): s+=C(372+i*92,350,30,c,c,0)
    s+=T(330,416,260)+T(330,436,170,DIM)
    return s
T_['brand-guidelines-mini-site']=t1
# 2 stream title cards
def t2():
    s=R(150,90,660,372,22)+H(176,116,608,230,BL)
    s+=C(200,142,9,CO,CO,0)+fade(C(200,142,9,BG,CO,0),[0,1,0,1,0],D)
    s+=mv(R(176,300,330,86,14,BG,LI,4)+T(200,326,200,LI,16)+T(200,356,130,L,10),[(-420,0),(-420,0),(0,0),(0,0),(-420,0),(-420,0)],D)
    s+=T(176,410,300)+T(176,430,180,DIM)+C(752,416,16,'none',L,4)
    return s
T_['stream-title-cards']=t2
# 3 drifting cursors
def t3():
    s=R(130,80,700,380,22)+H(160,110,300,170,BL)+R(500,110,300,80,14)+T(524,138,160)+T(524,160,100,DIM)+R(500,210,300,70,14,'none',DIM,3)+R(160,310,200,110,14,'none',DIM,3)+R(390,310,410,110,14)+T(414,340,180)+T(414,364,260,DIM)
    s+=fade(C(645,345,30,'none',CO,4),[0,0,1,0,0],D)
    s+=mv(cursor(220,210)+cursor(0,0).replace('fill="%s"'%L,'fill="%s"'%CO)*0,[(0,0),(430,170),(430,170),(300,-60),(0,0)],D)
    return s
T_['soft-drifting-cursor']=t3
# 4 line icons (stroke draws)
def draw(d,c):
    return P(d,'none',c,7,'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'+'<animate attributeName="stroke-dashoffset" dur="%ss" repeatCount="indefinite" keyTimes="0;.3;.8;1" values="1;0;0;1" calcMode="spline" keySplines=".45 0 .25 1;.45 0 .25 1;.45 0 .25 1"/'.replace('>','')+'' ) if False else \
        '<path d="%s" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" dur="%ss" repeatCount="indefinite" keyTimes="0;.3;.8;1" values="1;0;0;1" calcMode="spline" keySplines=".45 0 .25 1;.45 0 .25 1;.45 0 .25 1"/></path>'%(d,c,D)
def t4():
    s=''
    for i,(cx,c) in enumerate(((220,CO),(480,LI),(740,BL))):
        s+=C(cx,250,100,'none',DIM,4)
    s+=draw('M220 180 a70 70 0 1 0 0.1 0 M150 250 h140 M220 180 q-40 70 0 140 q40 -70 0 -140',CO)
    s+=draw('M440 310 l8 -34 l76 -76 l26 26 l-76 76 z M504 214 l26 26',LI)
    s+=draw('M670 250 q70 -80 140 0 q-70 80 -140 0 z M740 250 m-16 0 a16 16 0 1 0 32 0 a16 16 0 1 0 -32 0',BL)
    s+=T(120,420,200,DIM)+T(380,420,200,DIM)+T(640,420,200,DIM)
    return s
T_['line-icon-animations']=t4
# 5 brand audit
def t5():
    s=''
    cols=[LI,LI,CO,LI,YE,LI]
    for i,c in enumerate(cols):
        x=130+(i%3)*232; y=90+(i//3)*190
        s+=H(x,y,200,110,BL if c!=CO else CO,12)+T(x,y+128,120)+C(x+176,y+137,12,c,c,0)
    s+=mv(F(110,70,740,6,CO,3)+'',[(0,0),(0,380),(0,0)],D)
    return s
T_['brand-audit-engine']=t5
# 6 session to skill
def t6():
    s=R(110,100,300,340,20)
    for i,(w,c) in enumerate(((180,L),(220,DIM),(150,L),(200,DIM))):
        s+=fade(R(136,130+i*74,w,52,14,'none',c,3),[0,1,1,1,1],D,i*0.0)
    s+=P('M430 270 h90 m-24 -24 l24 24 l-24 24','none',CO,6)
    s+=mv(C(430,270,10,CO,CO,0),[(0,0),(80,0),(0,0)],D)
    s+=R(550,100,300,340,20,'none',LI,4)+T(584,140,150,LI,14)+T(584,184,220)+T(584,208,200,DIM)+T(584,232,230,DIM)+T(584,256,120,DIM)+H(584,300,232,100,LI)
    return s
T_['session-to-skill']=t6
# 7 generator to figma plugin
def t7():
    s=R(100,100,260,340,20)
    for i in range(4):
        y=150+i*72; s+=T(130,y,200,DIM,8)+mv(C(150,y+4,13,CO,CO,0),[(0,0),(60+i*20,0),(20,0),(0,0)],D)
    s+=P('M385 270 h80 m-22 -22 l22 22 l-22 22','none',L,6)
    s+=R(490,100,370,340,20,'none',BL,4)
    s+=H(520,130,150,120,BL)+R(690,130,140,120,12)+fade(F(700,140,120,100,CO,8),[0,0,1,1,0],D)+R(520,270,310,140,12,'none',DIM,3)
    s+=P('M520 130 v0','none',L,0)
    return s
T_['generator-to-figma-plugin']=t7
# 8 product feature spot
def t8():
    card=R(310,120,340,300,24,BG,L,4)+H(334,144,292,150,BL,12)+T(334,320,200)+T(334,346,140,DIM)+F(334,376,110,26,CO,13)
    s=fade(G(card),[1,1,0,0,1],D)
    mock=R(310,120,340,300,24,'#1d2036',L,4)+F(334,144,292,150,BL,12)+C(480,219,38,YE,YE,0)+T(334,320,200,L)+T(334,346,140,DIM)+F(334,376,110,26,CO,13)
    s+=fade(G(mock),[0,0,1,1,0],D)
    return s
T_['product-feature-spot']=t8
# 9 paid ad pipeline
def t9():
    s=''
    for i,c in enumerate((BL,YE,CO)):
        x=100+i*270
        s+=R(x,150,200,240,20,'none',L,4)+H(x+22,174,156,100,c,10)+T(x+22,300,120)+T(x+22,324,80,DIM)
        if i<2: s+=P('M%g 270 h50 m-16 -16 l16 16 l-16 16'%(x+212),'none',DIM,5)
    s+=mv(C(300,270,12,LI,LI,0),[(0,0),(270,0),(540,0),(0,0)],D)
    return s
T_['paid-ad-pipeline']=t9
# 10 low poly
def t10():
    s=C(740,150,56,YE,YE,0)
    tri=[('M60 440 L260 170 L400 440Z',BL),('M260 170 L400 440 L300 440Z','#4569c9'),('M300 440 L520 230 L760 440Z',LI),('M520 230 L640 440 L420 440Z','#9fcb3b'),('M600 440 L780 300 L900 440Z',CO)]
    for d,c in tri: s+=P(d,c,BG,3)
    s+=fade(P('M260 170 L300 260 L220 260Z','none',L,4),[.2,1,.2],D)
    s+=P('M40 440 H920','none',L,4)
    return s
T_['lowpoly-3d-scene']=t10
# 11 prompt rewriter
def t11():
    s=R(100,110,330,320,20)+T(130,150,150)+T(130,176,90,DIM)+R(530,110,330,320,20,'none',LI,4)
    s+=P('M452 270 h54 m-18 -18 l18 18 l-18 18','none',CO,6)
    for i,w in enumerate((250,270,220,260,180)):
        s+=fade(mv(T(560,150+i*34,w,LI,10),[(-12,0),(0,0),(0,0),(-12,0)],D),[0,1,1,0],D,0)
    s+=F(130,376,110,30,L,15)
    return s
T_['metacognitive-prompt-rewriter']=t11
# 12 industry swapper
def t12():
    s=R(280,100,400,250,22)
    s+=fade(H(304,124,200,140,BL),[1,1,0,0,1],D)+fade(H(304,124,200,140,CO),[0,0,1,1,0],D)
    s+=T(530,134,120)+T(530,162,110,DIM)+T(530,190,80,DIM)+T(304,288,240)+T(304,312,160,DIM)
    for i,c in enumerate((BL,CO,LI,YE,PK)):
        s+=C(300+i*90,430,26,c,c,0)
    s+=mv(C(300,430,36,'none',L,4),[(0,0),(0,0),(90,0),(180,0),(270,0),(0,0)],D)
    return s
T_['industry-swapper']=t12
# 13 widows
def t13():
    s=R(180,90,600,360,22)
    for i in range(5): s+=T(220,140+i*48,520,L,12)
    s+=T(220,380,520,L,12)
    s+=fade(T(220,428,60,CO,12),[1,1,0,0,1],D)
    s+=fade(T(220,428,260,LI,12),[0,0,1,1,0],D)
    return s.replace('<rect x="220" y="332"','<rect x="220" y="332"')
T_['avoid-widows-and-orphans']=t13
# 14 fields scan
def t14():
    s=R(220,70,520,400,22)
    for i in range(4):
        y=110+i*80; s+=T(250,y,120,DIM,8)+R(250,y+20,460,40,10,'none',L,3)
    s+=F(250,420,140,30,CO,15)
    s+=mv(F(232,92,496,14,LI,7).replace('/>',' opacity=".55"/>'),[(0,0),(0,330),(0,0)],D)
    for i in range(4):
        s+=fade(R(250,130+i*80,460,40,10,'none',LI,4),[0,0,1,1,0],D)
    return s
T_['fields-scan-overlay']=t14
# 15 ui mockup kit
def t15():
    s=R(110,80,740,380,22)+R(130,100,130,340,14,'none',DIM,3)
    for i in range(4): s+=T(148,130+i*40,90,DIM,8)
    for i,c in enumerate((BL,CO,LI)): s+=R(290+i*184,100,166,90,14,'none',c,4)+T(310+i*184,130,70,c,12)+T(310+i*184,154,100,DIM,8)
    for i,h in enumerate((60,110,80,150,100,130)):
        s+=mv(F(300+i*42,430-h,28,h,BL,6),[(0,0),(0,-18-i*3),(0,0)],D)
    s+=H(570,210,260,230,YE)
    return s
T_['brand-neutral-ui-mockup-kit']=t15
# 16 motion explainer
def t16():
    s=R(180,90,600,260,22)+H(210,120,250,200,BL)+C(600,220,70,'none',CO,5)+T(520,330,200,DIM,8)
    s+=P('M110 420 H850','none',DIM,4)
    for i,c in enumerate((BL,CO,LI,YE)): s+=R(130+i*180,398,150,44,10,'none',c,4)
    s+=mv(F(130,380,5,80,L,2),[(0,0),(690,0),(0,0)],D)
    return s
T_['motion-explainer']=t16
# 17 asset generator
def t17():
    s=R(90,90,250,360,20)
    for i in range(4): s+=T(116,140+i*70,196,DIM,8)+mv(C(136,144+i*70,13,LI,LI,0),[(0,0),(50,0),(10,0),(0,0)],D,i*0.2)
    s+=H(380,110,300,170,BL)+R(710,110,140,250,14)+F(710,110,140,250,'none',10) .replace('fill="none"','fill="url(#h%s)"'%CO[1:])+R(380,310,170,130,14,'none',YE,4)+R(580,310,100,130,14,'none',DIM,3)
    s+=fade(R(374,104,312,182,16,'none',CO,5),[1,1,0,0,1],D)+fade(R(704,104,152,262,16,'none',CO,5),[0,0,1,1,0],D)
    return s
T_['asset-generator-engine']=t17
# 18 scripted cursor
def t18():
    s=R(190,80,580,380,22)+R(220,110,200,340,12,'none',DIM,3)
    for i in range(4): s+=T(240,140+i*44,120,DIM,8)
    s+=H(450,110,290,150,BL)+R(450,290,290,70,14,'none',DIM,3)+F(560,390,150,40,CO,20)
    s+=fade(R(552,382,166,56,28,'none',LI,5),[0,0,1,0,0],D)
    s+=mv(cursor(260,200),[(0,0),(330,200),(330,200),(120,-30),(0,0)],D)
    return s
T_['scripted-cursor-demo']=t18
# 19 palette
def t19():
    cols=[BL,CO,LI,YE,PK]
    s=''
    for i,c in enumerate(cols): s+=C(190+i*145,160,52,c,c,0)
    s+=mv(C(190,160,64,'none',L,4),[(0,0),(0,0),(145,0),(290,0),(435,0),(0,0)],D)
    s+=R(150,280,660,170,22)
    s+=fade(H(176,306,280,118,BL),[1,1,0,0,1],D)+fade(H(176,306,280,118,CO),[0,0,1,1,0],D)
    s+=T(490,320,260)+T(490,346,200,DIM)+F(490,386,120,32,LI,16)
    return s
T_['palette-brand-constraints']=t19
# 20 tile to fullscreen
def t20():
    s=''
    for i,c in enumerate((BL,CO,LI)):
        x=110+i*250
        s+=fade(R(x,130,220,280,18)+H(x+18,150,184,130,c,10)+T(x+18,306,120)+T(x+18,330,80,DIM),[1,1,0,0,1],D)
    big=R(110,60,740,420,22,BG,LI,4)+H(140,90,320,360,CO,14)+T(500,120,280,L,14)+T(500,160,220,DIM)+T(500,184,250,DIM)+T(500,208,190,DIM)
    s+=fade(big,[0,0,1,1,0],D)
    return s
T_['tile-to-fullscreen']=t20
# 21 cut products
def t21():
    bottle=P('M0 0 h60 v30 q30 20 30 70 v170 q0 20 -20 20 h-80 q-20 0 -20 -20 v-170 q0 -50 30 -70z','none',L,4)
    s=R(100,90,340,360,20,'none',DIM,3)+H(120,110,300,320,DIM,12)+G(bottle,'transform="translate(210,150)"')
    s+=P('M470 270 h60 m-18 -18 l18 18 l-18 18','none',CO,6)
    s+=R(560,90,300,360,20,'none',LI,4)
    b=G(F(0,0,0,0,'none'))
    s+=G(P('M0 0 h60 v30 q30 20 30 70 v170 q0 20 -20 20 h-80 q-20 0 -20 -20 v-170 q0 -50 30 -70z',YE,L,4)+F(-4,150,98,70,CO,8),'transform="translate(645,150)"')
    s+=fade(P('M645 150 h60 v30 q30 20 30 70 v170 q0 20 -20 20 h-80 q-20 0 -20 -20 v-170 q0 -50 30 -70z','none',CO,5,'stroke-dasharray="14 10"'),[1,.2,1],D)
    return s
T_['cut-out-products']=t21
# 22 figma to motion page
def t22():
    s=R(100,100,330,340,6,'none',BL,3)
    for x,y in ((100,100),(430,100),(100,440),(430,440)): s+=F(x-8,y-8,16,16,BG,2)+R(x-8,y-8,16,16,2,'none',BL,3)
    s+=H(130,130,270,110,BL)+T(130,270,200)+T(130,296,140,DIM)+F(130,340,90,28,CO,14)
    s+=P('M470 270 h60 m-18 -18 l18 18 l-18 18','none',L,6)
    s+=R(560,100,300,340,20)
    s+=mv(H(586,130,248,110,BL),[(0,40),(0,0),(0,0),(0,40)],D)
    s+=fade(mv(T(586,270,200),[(40,0),(0,0),(0,0),(40,0)],D),[0,1,1,0],D)+fade(mv(T(586,296,140,DIM),[(40,0),(0,0),(0,0),(40,0)],D),[0,1,1,0],D)
    s+=mv(F(586,340,90,28,CO,14),[(0,60),(0,0),(0,0),(0,60)],D)
    return s
T_['figma-to-motion-page']=t22

if __name__=='__main__':
    for k,f in T_.items():
        open(os.path.join(OUT,k+'.svg'),'w').write(wrap(f()))
    print(len(T_),'written')
