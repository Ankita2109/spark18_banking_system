
import json
from login_manage import loginManage


if __name__ == '__main__':
    with open("config.json", "r") as config_file :
        config = json.load(config_file)
    lm =loginManage()
    lm.input_values()

