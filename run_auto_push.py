import subprocess
from datetime import datetime

if datetime.now().weekday() == 3:
    subprocess.run(["bash", "/home/joaopaiva/Maringa-Housing-Prices/auto_push.sh"])
else:
    print("Today is not Friday. No push was made.")