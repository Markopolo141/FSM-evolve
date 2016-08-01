import click
import json

import logging
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)

@click.command()
@click.argument('config', type=click.File('r'))
@click.argument('in_file', type=click.File('r'))
@click.argument('out_file')
def loadSim(config, in_file, out_file):
    logger.info("Reading config")
    config_text = config.read()
    config.close()
    logger.info("parsing config json")
    try:
        config = json.loads(config_text)
    except:
        logger.error("Failed to parse config file as valid JSON")
        raise
    assert "sets" in config, "config file needs to contain 'sets' parameter"
    assert isinstance(config['sets'], list), "config file needs 'sets' to be a list"
    for s in config['sets']:
        assert isinstance(s, dict), "each entry in 'sets' needs to be a dictionary of keys and their replacements"
    
    logger.info("reading input file")
    in_text = in_file.read()
    in_file.close()
    for i,s in enumerate(config['sets']):
        logger.info("applying set {}".format(i+1))
        for old_string, new_string in s.iteritems():
            in_text = in_text.replace(old_string, new_string)
    logger.info("outputting")
    out = open(out_file, "w")
    out.write(in_text)
    out.close()
    logger.info("done")

if __name__ == '__main__':
    loadSim()
