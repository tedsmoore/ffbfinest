import requests
from datetime import datetime


def an_example():
    print("it worked!")


def get_adp_ppr_fp():
    date = datetime.now()

    res = requests.get('https://www.fantasypros.com/nfl/adp/ppr-overall.php')
    content = res.content

    with open(f'../static/data/{date.strftime("%Y%m%d")}_adp_ppr_fp', 'w') as f:
        f.write(content)
