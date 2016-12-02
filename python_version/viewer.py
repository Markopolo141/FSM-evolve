import click
import json
from copy import deepcopy as copy

matrix = None

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
    
    range_subs = config['range_substitutions']
    square_diff=50
    border_diff=30
    square_spacing=0
    dims = [(k['max']-k['min']+0.0000001)/k['step'] for j,k in range_subs]
    
    def gen_matrix(dims):
        matrix = None
        for d in dims[::-1]:
            matrix = [copy(matrix) for i in range(int(d)+1)]
        return matrix
    def get_coords(dictionary):
        c = []
        for j,k in range_subs:
            c.append(int((dictionary[j]-k['min'])/k['step']))
        return c
    def set_from_coordinates(matrix,c,val):
        m = matrix
        for cc in c[:-1]:
            m = m[cc]
        m[c[-1]] = val
    def get_from_coordinates(matrix,c):
        m = matrix
        for cc in c:
            m = m[cc]
        return m
#    def diagnostic_human(v):
#        vs = v['pops'][0][:-1]
#        D = ["FIM","FNM","CIM","CNM","FIF","FNF","CIF","CNF"]
#        Z = zip(vs,D)
#        Z = [z for z in Z if z[0]>0.1]
#        return "-".join([z[1] for z in Z])
    def diagnostic_machine(v):
        if not v:
            #return "#0000FF"
            return "#EEEEEE"
        else:
            v = v['pops'][0]
            vs = v[:-1]
            #D = ["FF","AA","55","00","FF","AA","55","00"]
            D = ["00","44","88","CC","00","44","88","CC"]
            Z = zip(vs,D)
            Z = [z for z in Z if z[0]>0.1]
            return "#"+"".join([z[1] for z in Z])+"AA"
    def calc_stats(dims):
        x_dims = dims[0::2]
        y_dims = dims[1::2]
        x_m_dims = [square_diff]
        y_m_dims = [square_diff]
        for i,r in enumerate(x_dims):
            x_m_dims.append(int(r+1)*x_m_dims[-1] + (i+1)*border_diff)
        for i,r in enumerate(y_dims):
            y_m_dims.append(int(r+1)*y_m_dims[-1] + (i+1)*border_diff)
        return x_m_dims,y_m_dims
    def get_offset(x_m_dims,y_m_dims, v):
        x_v = v[0::2]
        y_v = v[1::2]
        x = sum([x_v[i]*x_m_dims[i] for i in range(len(x_v))])
        y = sum([y_v[i]*y_m_dims[i] for i in range(len(y_v))])
        return x,y
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
    
    matrix = gen_matrix(dims)
    for o in data['output']:
        set_from_coordinates(matrix,get_coords(o['parameters']),{"pops":o['pops']})
    output_string = ""
    x_m_dims,y_m_dims = calc_stats(dims)
    max_x = 0
    max_y = 0
    for a in iterate(matrix):
        xoff = 0#(len(x_m_dims)-1)*border_diff
        yoff = 0#(len(y_m_dims)-1)*border_diff
        x,y = get_offset(x_m_dims,y_m_dims,a)
        x += xoff
        y += yoff
        if x>max_x:
            max_x = x
        if y>max_y:
            max_y = y
        output_string = output_string + '<rect x="{0}" y="{1}" width="{2}" height="{2}" fill="{3}"></rect>\n'.format(x+square_spacing,y+square_spacing,square_diff-square_spacing, diagnostic_machine(get_from_coordinates(matrix,a)))

    output.write('<svg width="{0}" height="{1}"><rect x="0" y="0" width="{0}" height="{1}" fill="white"></rect>\n'.format(max_x+square_diff,max_y+square_diff))
#    range_subs_x = range_subs[0::2]
#    range_subs_y = range_subs[1::2]
#    x_dims = dims[0::2]
#    y_dims = dims[1::2]
#    for i in range(len(x_dims)):
#        norm_y = (len(x_dims)-i-0.5)*border_diff
#        min_x = (len(y_m_dims)-1)*border_diff
#        max_x = (len(y_m_dims)-1)*border_diff + (x_dims[i]+1)*x_m_dims[i]
#        ext_y = (len(x_dims)-i-0.1)*border_diff
#        output_string += '<text x="{}" y="{}" font-size="30">{}</text>'.format((min_x+max_x)/2.0, norm_y, "hello")
#        output_string += '<line x1="{1}" y1="{0}" x2="{2}" y2="{0}" stroke="black" opacity="100%" stroke-width="3"></line>'.format(norm_y, min_x, max_x)
#        output_string += '<line x1="{1}" y1="{0}" x2="{1}" y2="{2}" stroke="black" opacity="100%" stroke-width="3"></line>'.format(norm_y, min_x, ext_y)
#        output_string += '<line x1="{1}" y1="{0}" x2="{1}" y2="{2}" stroke="black" opacity="100%" stroke-width="3"></line>'.format(norm_y, max_x, ext_y)
#    for i in range(len(y_dims)):
#        norm_x = (len(y_dims)-i-0.5)*border_diff
#        min_y = (len(x_m_dims)-1)*border_diff
#        max_y = (len(x_m_dims)-1)*border_diff + (y_dims[i]+1)*y_m_dims[i]
#        ext_x = (len(y_dims)-i-0.1)*border_diff
#        output_string += '<text x="{}" y="{}" font-size="30">{}</text>'.format((min_y+max_y)/2.0, norm_x, "hello")
#        output_string += '<line x1="{1}" y1="{0}" x2="{2}" y2="{0}" stroke="black" opacity="100%" stroke-width="3"></line>'.format(norm_x, min_y, max_y)
#        output_string += '<line x1="{1}" y1="{0}" x2="{1}" y2="{2}" stroke="black" opacity="100%" stroke-width="3"></line>'.format(norm_x, min_y, ext_x)
#        output_string += '<line x1="{1}" y1="{0}" x2="{1}" y2="{2}" stroke="black" opacity="100%" stroke-width="3"></line>'.format(norm_x, max_y, ext_x)
    output.write(output_string)
    output.write("</svg>")
    output.flush()
    output.close()
    print "DONE"

if __name__ == '__main__':
    view()