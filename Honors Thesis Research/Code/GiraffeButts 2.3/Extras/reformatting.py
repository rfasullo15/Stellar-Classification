import pandas as pd

file_path = "C:\Users\90rfa\Documents\Honors Thesis Data\data_v2_Extras\AllObs_SpecData_Formatted.txt"

data = pd.read_csv(file_path, delim_whitespace = True, usecols=[1,2,3,4])


index = 0
while index< len(data["dummy"].values):
    val = data["dummy"][index]
    if val == "5":
        data["dummy"][index] = "005"
    elif val == "1108":
        data["dummy"][index] = "_1108"
    elif val == "9676A":
        data["typed"][index] = "3CenA"
        data["dummy"][index] = ""
    elif val == "9676B":
        data["typed"][index] = "3CenB"
        data["dummy"][index] = ""
    else:
        data["dummy"][index] = val.zfill(6)

    index +=1

df = pd.DataFrame()
df["name"] = data["typed"] + data["dummy"]
df["classification"] = data["ident"] + data["Tc1"]

df.to_csv("Classifications_ALL.txt", index= False, sep = "\t")
