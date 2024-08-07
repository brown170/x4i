import x4i
import csv
udict = x4i.get_exfor_dict('025')
with open('exfor_units.csv', mode='w') as csvfile:
    csvwriter = csv.writer(csvfile)
    for k,v in udict.items():
        csvwriter.writerow([k, v['expansion'], v['comment']])
