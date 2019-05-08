import csv

endl = "\n"
def saveas(fname, data):
    if fname == "":
        return
    if not fname[-1:-5:-1] == "vsc.":
        fname += ".csv"


    rows = data.split("-"*20+endl)
    table = [row.split(endl) for row in rows]
    titles = []
    #create title row for table
    for cell in table[0]:
        titlestr = ""
        for letter in cell:
            titlestr += letter
            if letter == ":":
                titles.append(titlestr)
                break

    #delete titles from individual rows
    for i in range(len(table)):
        for j in range(len(table[i])):
            table[i][j] = table[i][j][table[i][j].find(":")+1:]

    #attatch titles
    table = [titles] + table
    with open(fname, "w+") as csvfile:
        writer = csv.writer(csvfile)
        for row in table:
            writer.writerow(row)
