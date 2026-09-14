from graphviz import Digraph
from pathlib import Path

OUT = Path(__file__).parent

# ---------- Modelo conceptual en notacion Chen ----------
g = Digraph('conceptual', engine='dot')
g.attr(rankdir='LR', splines='spline', overlap='false', nodesep='0.45', ranksep='1.1', pad='0.25', bgcolor='white')
g.attr('graph', label='Modelo conceptual ampliado - Notacion de Chen', labelloc='t', fontsize='22', fontname='Arial')
g.attr('node', fontname='Arial', fontsize='10', color='black', style='solid')
g.attr('edge', fontname='Arial', fontsize='9', color='black', dir='none')

def entity(name, label=None):
    g.node(name, label or name, shape='box', fontsize='11')

def relation(name, label=None):
    g.node(name, label or name, shape='diamond', fontsize='9', margin='0.08')

def attr(name, label, key=False, multi=False):
    lab = f'<<U>{label}</U>>' if key else label
    g.node(name, lab, shape='ellipse', peripheries='2' if multi else '1', fontsize='9')

def attach(ent, attrs):
    for a in attrs:
        g.edge(ent, a)

def rel(a, r, b, card_a, card_b):
    # a -- relation -- b. Cardinalidad escrita en cada lado.
    g.edge(a, r, label=card_a)
    g.edge(r, b, label=card_b)

# Entidades base
for n in ['USUARIOS','CATEGORIAS','EVENTOS','LOG_ACCESOS','UBICACIONES','TIPOS_DISPONIBILIDAD','DISPONIBILIDADES','TAREAS']:
    entity(n)

# Atributos base
for n,l,k,m in [
    ('u_id','id_usuario',True,False),('u_nombre','nombre',False,False),('u_apellido','apellido',False,False),
    ('u_fecha','fecha_registro',False,False),('u_activo','activo',False,False),('u_tel','telefonos',False,True),('u_email','emails',False,True),
]: attr(n,l,k,m)
attach('USUARIOS',['u_id','u_nombre','u_apellido','u_fecha','u_activo','u_tel','u_email'])

for n,l,k in [('c_id','id_categoria',True),('c_nombre','nombre',False)]: attr(n,l,k)
attach('CATEGORIAS',['c_id','c_nombre'])

for n,l,k in [('e_id','id_evento',True),('e_titulo','titulo',False),('e_desc','descripcion',False),('e_ini','fecha_inicio',False),('e_fin','fecha_fin',False)]: attr(n,l,k)
attach('EVENTOS',['e_id','e_titulo','e_desc','e_ini','e_fin'])

for n,l,k in [('l_id','id_log',True),('l_fecha','fecha_acceso',False)]: attr(n,l,k)
attach('LOG_ACCESOS',['l_id','l_fecha'])

# Atributos modulos nuevos
for n,l,k in [('ub_id','id_ubicacion',True),('ub_nom','nombre',False),('ub_dir','direccion',False),('ub_ciu','ciudad',False),('ub_cap','capacidad',False)]: attr(n,l,k)
attach('UBICACIONES',['ub_id','ub_nom','ub_dir','ub_ciu','ub_cap'])

for n,l,k in [('td_id','id_tipo_disponibilidad',True),('td_nom','nombre',False)]: attr(n,l,k)
attach('TIPOS_DISPONIBILIDAD',['td_id','td_nom'])

for n,l,k in [('d_id','id_disponibilidad',True),('d_fecha','fecha',False),('d_hi','hora_inicio',False),('d_hf','hora_fin',False)]: attr(n,l,k)
attach('DISPONIBILIDADES',['d_id','d_fecha','d_hi','d_hf'])

for n,l,k in [('t_id','id_tarea',True),('t_tit','titulo',False),('t_des','descripcion',False),('t_pri','prioridad',False),('t_lim','fecha_limite',False),('t_est','estado',False)]: attr(n,l,k)
attach('TAREAS',['t_id','t_tit','t_des','t_pri','t_lim','t_est'])

# Relaciones
for r,l in [
    ('R_PROP','PROPIETARIO'),('R_PERT','PERTENECE'),('R_PART','PARTICIPACION'),('R_JER','JERARQUIA'),('R_REG','REGISTRA'),
    ('R_UBI','SE REALIZA EN'),('R_DISP','TIENE'),('R_TIPO','CLASIFICA'),('R_TAREA','CONTIENE'),('R_RESP','RESPONSABLE')
]: relation(r,l)

rel('USUARIOS','R_PROP','EVENTOS','1','N')
rel('CATEGORIAS','R_PERT','EVENTOS','1','N')
rel('UBICACIONES','R_UBI','EVENTOS','1','N')
rel('USUARIOS','R_DISP','DISPONIBILIDADES','1','N')
rel('TIPOS_DISPONIBILIDAD','R_TIPO','DISPONIBILIDADES','1','N')
rel('EVENTOS','R_TAREA','TAREAS','1','N')
rel('USUARIOS','R_RESP','TAREAS','1','N')
rel('USUARIOS','R_REG','LOG_ACCESOS','1','N')
# N:M participacion
rel('USUARIOS','R_PART','EVENTOS','N','M')
attr('p_rol','rol',False); attr('p_estado','estado_confirmacion',False)
g.edge('R_PART','p_rol'); g.edge('R_PART','p_estado')
# Relacion recursiva: dos roles de la misma entidad
# usar dos aristas paralelas con labels claros
g.edge('CATEGORIAS','R_JER', label='padre 1', constraint='false')
g.edge('CATEGORIAS','R_JER', label='hija N', constraint='false')

# Ayuda de agrupacion visual
g.attr(rank='same')
# render
g.save(str(OUT/'modelo_conceptual_chen.dot'))
g.render(filename='modelo_conceptual_chen', directory=str(OUT), format='png', cleanup=False)

# ---------- Modelo logico ----------
l = Digraph('logico', engine='dot')
l.attr(rankdir='LR', splines='polyline', nodesep='0.55', ranksep='0.9', pad='0.2', bgcolor='white')
l.attr('graph', label='Modelo logico ampliado', labelloc='t', fontsize='22', fontname='Arial')
l.attr('node', shape='plain', fontname='Arial', fontsize='9')
l.attr('edge', fontname='Arial', fontsize='8', color='black', arrowsize='0.7')

def table_node(name, title, rows):
    tr = ''.join(f'<TR><TD ALIGN="LEFT">{r}</TD></TR>' for r in rows)
    label=f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
    <TR><TD BGCOLOR="#DDDDDD"><B>{title}</B></TD></TR>{tr}</TABLE>>'''
    l.node(name,label=label)

table_node('usuarios','USUARIOS',[
    '<B>PK</B> id_usuario','nombre','apellido','fecha_registro','activo'])
table_node('telefonos','USUARIO_TELEFONOS',[
    '<B>PK/FK</B> id_usuario -&gt; USUARIOS.id_usuario','<B>PK</B> telefono'])
table_node('emails','USUARIO_EMAILS',[
    '<B>PK/FK</B> id_usuario -&gt; USUARIOS.id_usuario','<B>PK</B> email'])
table_node('categorias','CATEGORIAS',[
    '<B>PK</B> id_categoria','nombre','<B>FK</B> id_categoria_padre -&gt; CATEGORIAS.id_categoria'])
table_node('ubicaciones','UBICACIONES [NUEVA]',[
    '<B>PK</B> id_ubicacion','nombre','direccion','ciudad','capacidad'])
table_node('eventos','EVENTOS [AMPLIADA]',[
    '<B>PK</B> id_evento','<B>FK</B> id_usuario_propietario -&gt; USUARIOS.id_usuario',
    '<B>FK</B> id_categoria -&gt; CATEGORIAS.id_categoria','<B>FK</B> id_ubicacion -&gt; UBICACIONES.id_ubicacion',
    'titulo','descripcion','fecha_inicio','fecha_fin'])
table_node('part','PARTICIPACIONES',[
    '<B>PK/FK</B> id_evento -&gt; EVENTOS.id_evento','<B>PK/FK</B> id_invitado -&gt; USUARIOS.id_usuario','rol','estado_confirmacion'])
table_node('log','LOG_ACCESOS',[
    '<B>PK</B> id_log','<B>FK</B> id_usuario -&gt; USUARIOS.id_usuario','fecha_acceso'])
table_node('tipos','TIPOS_DISPONIBILIDAD [NUEVA]',[
    '<B>PK</B> id_tipo_disponibilidad','<B>UNIQUE</B> nombre'])
table_node('disp','DISPONIBILIDADES [NUEVA]',[
    '<B>PK</B> id_disponibilidad','<B>FK</B> id_usuario -&gt; USUARIOS.id_usuario','fecha','hora_inicio','hora_fin',
    '<B>FK</B> id_tipo_disponibilidad -&gt; TIPOS_DISPONIBILIDAD.id_tipo_disponibilidad'])
table_node('tareas','TAREAS [NUEVA]',[
    '<B>PK</B> id_tarea','<B>FK</B> id_evento -&gt; EVENTOS.id_evento','<B>FK</B> id_usuario_responsable -&gt; USUARIOS.id_usuario',
    'titulo','descripcion','prioridad','fecha_limite','estado'])

# FK child -&gt; parent
for child,parent,label in [
    ('telefonos','usuarios','id_usuario'),('emails','usuarios','id_usuario'),('categorias','categorias','id_categoria_padre'),
    ('eventos','usuarios','propietario'),('eventos','categorias','categoria'),('eventos','ubicaciones','ubicacion'),
    ('part','eventos','id_evento'),('part','usuarios','id_invitado'),('log','usuarios','id_usuario'),
    ('disp','usuarios','id_usuario'),('disp','tipos','tipo'),('tareas','eventos','id_evento'),('tareas','usuarios','responsable')
]:
    l.edge(child,parent,label=label)

l.save(str(OUT/'modelo_logico.dot'))
l.render(filename='modelo_logico', directory=str(OUT), format='png', cleanup=False)

# ---------- Modelo fisico ----------
p = Digraph('fisico', engine='dot')
p.attr(rankdir='LR', splines='polyline', nodesep='0.55', ranksep='0.9', pad='0.2', bgcolor='white')
p.attr('graph', label='Modelo fisico PostgreSQL - esquema prototipo', labelloc='t', fontsize='22', fontname='Arial')
p.attr('node', shape='plain', fontname='Arial', fontsize='8.7')
p.attr('edge', fontname='Arial', fontsize='8', color='black', arrowsize='0.7')

def ptable(name,title,rows):
    tr=''.join(f'<TR><TD ALIGN="LEFT">{r}</TD></TR>' for r in rows)
    label=f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
    <TR><TD BGCOLOR="#DDDDDD"><B>{title}</B></TD></TR>{tr}</TABLE>>'''
    p.node(name,label=label)

ptable('usuarios','usuarios',[
    'id_usuario SERIAL PK','nombre VARCHAR(50) NOT NULL','apellido VARCHAR(50) NOT NULL',
    'fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE','activo BOOLEAN NOT NULL DEFAULT TRUE'])
ptable('telefonos','usuario_telefonos',[
    'id_usuario INTEGER NOT NULL PK/FK','telefono VARCHAR(20) NOT NULL PK'])
ptable('emails','usuario_emails',[
    'id_usuario INTEGER NOT NULL PK/FK','email VARCHAR(100) NOT NULL PK'])
ptable('categorias','categorias',[
    'id_categoria SERIAL PK','nombre VARCHAR(50) NOT NULL','id_categoria_padre INTEGER FK NULL'])
ptable('ubicaciones','ubicaciones',[
    'id_ubicacion SERIAL PK','nombre VARCHAR(100) NOT NULL','direccion VARCHAR(200) NOT NULL',
    'ciudad VARCHAR(100) NOT NULL','capacidad INTEGER NOT NULL CHECK (capacidad &gt; 0)'])
ptable('eventos','eventos',[
    'id_evento SERIAL PK','id_usuario_propietario INTEGER FK NOT NULL','id_categoria INTEGER FK NOT NULL',
    'id_ubicacion INTEGER FK NOT NULL','titulo VARCHAR(100) NOT NULL','descripcion TEXT NULL',
    'fecha_inicio TIMESTAMP NOT NULL','fecha_fin TIMESTAMP NOT NULL','CHECK (fecha_fin &gt; fecha_inicio)'])
ptable('part','participaciones',[
    'id_evento INTEGER PK/FK ON DELETE CASCADE','id_invitado INTEGER PK/FK','rol VARCHAR(50) NULL',
    'estado_confirmacion VARCHAR(20) NOT NULL DEFAULT pendiente','CHECK estado: aceptado / pendiente / rechazado'])
ptable('log','log_accesos',[
    'id_log SERIAL PK','id_usuario INTEGER FK NOT NULL','fecha_acceso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'])
ptable('tipos','tipos_disponibilidad',[
    'id_tipo_disponibilidad SERIAL PK','nombre VARCHAR(30) NOT NULL UNIQUE'])
ptable('disp','disponibilidades',[
    'id_disponibilidad SERIAL PK','id_usuario INTEGER FK NOT NULL','fecha DATE NOT NULL','hora_inicio TIME NOT NULL',
    'hora_fin TIME NOT NULL','id_tipo_disponibilidad INTEGER FK NOT NULL','CHECK (hora_fin &gt; hora_inicio)'])
ptable('tareas','tareas',[
    'id_tarea SERIAL PK','id_evento INTEGER FK NOT NULL','id_usuario_responsable INTEGER FK NOT NULL',
    'titulo VARCHAR(120) NOT NULL','descripcion TEXT NULL','prioridad VARCHAR(30) NOT NULL','fecha_limite DATE NOT NULL',
    'estado VARCHAR(20) NOT NULL DEFAULT Pendiente','CHECK estado: Pendiente / En progreso / Completada / Cancelada'])

for child,parent,label in [
    ('telefonos','usuarios','FK'),('emails','usuarios','FK'),('categorias','categorias','FK recursiva'),
    ('eventos','usuarios','FK propietario'),('eventos','categorias','FK categoria'),('eventos','ubicaciones','FK ubicacion'),
    ('part','eventos','FK'),('part','usuarios','FK'),('log','usuarios','FK'),
    ('disp','usuarios','FK'),('disp','tipos','FK'),('tareas','eventos','FK'),('tareas','usuarios','FK')
]: p.edge(child,parent,label=label)

p.save(str(OUT/'modelo_fisico.dot'))
p.render(filename='modelo_fisico', directory=str(OUT), format='png', cleanup=False)

print('Modelos generados en', OUT)
