import yaml
import os

from parsers import GParser

with open('config.yaml') as f:
    config = yaml.safe_load(f)

if config['general']['filepath'] == 'default':
    config['general']['filepath']=os.path.join(os.path.dirname(__file__), 'root')

if config['general']['csvpath'] == 'default':
    config['general']['csvpath'] = os.path.dirname(__file__)

parser = GParser(config)
parser.run()