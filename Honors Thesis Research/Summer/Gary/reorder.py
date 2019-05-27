def readdata(filename):

    names = []
    tobesorted = []

    values = []
    file = open(filename, "r")
    for line in file:
        temp = line.strip("\n").split(",")
        names.append(temp[len(temp) - 1])
        if line[0] != ",":
            tobesorted.append(temp[0:2])
    return names, tobesorted

def formatname(lst):
    names = []
    for val in lst:
        if val[0][0] == "H":
            names.append(("HD" + val[0].strip("*").split(" ")[1].rjust(6, '0'), val[1]))
        else:
            names.append((val[0], val[1]))
    return names

def assigntypes(typelist, namelist):
    count = 0
    while count<len(typelist):
        index = 0
        while index < len(namelist):
            if typelist[count][0] == namelist[index]:
                namelist[index] = (namelist[index], typelist[count][1])
            index +=1
        count +=1

    count = 0
    while count<len(namelist):
        if type(namelist[count]) is str:
            namelist[count] = (namelist[count], "")
        count +=1
            
    return namelist

def write (srted):
    import csv
    file = open("gary.csv", "w", newline = '')
    wr = csv.writer(file, dialect = 'excel')
    wr.writerows(srted)
    

names, tobesorted = readdata("parallax.csv")
tobesorted = formatname(tobesorted)

srted = assigntypes(tobesorted, names)

write(srted)

