import sys
from spectacuplot import Spectacuplot

app = Spectacuplot()

for i in range(1, len(sys.argv)):
    app.open(sys.argv[i])

app.mainloop()