import click

@click.command()
@click.argument('infile', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
@click.argument('key')
def run(infile,outfile,key):
    key = str(key)
    counting = False
    line = infile.readline()
    #import pdb
    #pdb.set_trace()
    while line != "":
        if len(line) > 6:
            if line[0:6] == "File: ":
                if key in line:
                    counting = True
                else:
                    counting = False
        if counting:
            outfile.write(line)
        line = infile.readline()
    infile.close()
    outfile.flush()
    outfile.close()


if __name__ == '__main__':
    run()