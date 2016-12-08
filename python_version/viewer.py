import click
import json
from copy import deepcopy as copy

def access(m,c,val=None):
    for cc in c[:-1]:
        m = m[cc]
    if val is not None:
        m[c[-1]] = val
    m = m[c[-1]]
    return m

def iterate(matrix):
    V = []
    def inner_iterate(a,matrix):
        if isinstance(matrix,list):
            for i in range(len(matrix)):
                inner_iterate(a+[i],matrix[i])
        else:
            V.append(a)
    inner_iterate([],matrix)
    return V

class SVG(object):
    xmin = None
    xmax = None
    ymin = None
    ymax = None
    rects = None
    bg=None
    appends=None
    def __init__(self):
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.rects = []
        self.bg="white"
        self.appends = []
    def setBG(self,bg):
        self.bg=bg
    def addAppend(self,append):
        self.appends.append(append)
    def addRect(self,x,y,w,h,c):
        self.rects.append({"x":x,"y":y,"w":w,"h":h,"c":c})
        self.xmin = min(self.xmin,x) if self.xmin is not None else x
        self.ymin = min(self.ymin,y) if self.ymin is not None else y
        self.xmax = max(self.xmax,x+w) if self.xmax is not None else x+w
        self.ymax = max(self.ymax,y+h) if self.ymax is not None else y+h
    def flatten(self):
        s= '<svg width="{0}" height="{1}"><rect x="0" y="0" width="{0}" height="{1}" fill="{2}"></rect><g transform="translate({3} {4})">\n'.format(self.xmax-self.xmin,self.ymax-self.ymin,self.bg,-self.xmin,-self.ymin)
        for r in self.rects:
            s+='<rect x="{}" y="{}" width="{}" height="{}" fill="{}"></rect>\n'.format(r['x'],r['y'],r['w'],r['h'],r['c'])
        s+="</g>"
        for a in self.appends:
            s+=a+"\n"
        s+="</svg>"
        return s

def loadMatrix(data,config):
    range_subs = config['range_substitutions']
    dims = [(k['max']-k['min'])/k['step'] for j,k in range_subs]
    def get_coords(dictionary):
        c = []
        for j,k in range_subs:
            c.append(dictionary[j][1])
        return c
    matrix = None
    for d in dims[::-1]:
        matrix = [copy(matrix) for i in range(int(d)+1)]
    for o in data['output']:
        access(matrix,get_coords(o['parameters']),{"pops":o['pops']})
    return matrix

def outputSVG(matrix,config):
    svg = SVG()
    dims = [(k['max']-k['min'])/k['step'] for j,k in config['range_substitutions']]
    square_diff=config['svg']['square_diff']
    border_diff=config['svg']['border_diff']
    square_spacing=config['svg']['square_spacing']
    svg.setBG(config['svg']['colour']['background'])
    get_colour = eval(config['svg']['colour']['rule'])
    for a in config['svg'].get("appends",[]):
        svg.addAppend(a)
    def generateParameters(dims):
        x_dims = dims[0::2]
        y_dims = dims[1::2]
        x_m_dims = [square_diff]
        y_m_dims = [square_diff]
        for i,r in enumerate(x_dims):
            x_m_dims.append(int(r+1)*x_m_dims[-1] + (i+1)*border_diff)
        for i,r in enumerate(y_dims):
            y_m_dims.append(int(r+1)*y_m_dims[-1] + (i+1)*border_diff)
        return {"x_m_dims":x_m_dims,"y_m_dims":y_m_dims}
    def get_xy(v,parameters):
        x_v = v[0::2]
        y_v = v[1::2]
        x = sum([x_v[i]*parameters['x_m_dims'][i] for i in range(len(x_v))])
        y = sum([y_v[i]*parameters['y_m_dims'][i] for i in range(len(y_v))])
        return x,y
    parameters = generateParameters(dims)
    for a in iterate(matrix):
        x,y = get_xy(a,parameters)
        pops = access(matrix,a)
        if pops is None and config['svg']['colour']['none'] is not None:
            svg.addRect(
                x+square_spacing,
                y+square_spacing,
                square_diff-square_spacing,
                square_diff-square_spacing,
                config['svg']['colour']['none']
            )
        elif pops is not None:
            pops = pops['pops']
            for i,p in enumerate(pops):
                try:
                    svg.addRect(
                        x+square_spacing,
                        y+square_spacing + i*1.0/len(pops)*(square_diff-square_spacing),
                        square_diff-square_spacing,
                        1.0/len(pops)*(square_diff-square_spacing),
                        get_colour(p)
                    )
                except:
                    import pdb
                    pdb.set_trace()
                    raise
    return svg.flatten()

@click.command()
@click.argument('config', type=click.File('rb'))
@click.argument('data', type=click.File('rb'))
@click.argument('output', type=click.File('wb'))
def view(config,data,output):
    json_data = json.load(data)
    data.close()
    data = json_data
    config_data = json.load(config)
    config.close()
    config = config_data
    
    matrix = loadMatrix(data,config)
    output.write(outputSVG(matrix,config))
    output.flush()
    output.close()

if __name__ == '__main__':
    view()
