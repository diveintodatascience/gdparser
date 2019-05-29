import yaml

with open('config_.yaml') as f:
    config = yaml.safe_load(f)

parser = GParser(config)
parser.run()