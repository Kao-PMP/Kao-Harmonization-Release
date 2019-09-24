#!/usr/bin/env python3

# convert_stata.py <file.dta>
#
# croeder 10/2017

import sys
import re
import pandas as pd
FILE=sys.argv[1]
OUTFILE=re.sub('.dta', '.csv', FILE)


data = pd.io.stata.read_stata(FILE)
data.to_csv(OUTFILE)
