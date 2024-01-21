import json, os
from os.path import isfile, join, isdir
from PyPDF2 import PdfReader
from thefuzz import process
import shutil

full_data = {}; error_count = 0

project_path_main = 'P:/Projects_2021'

folder_list = [f'{f[:3]}-{f[5:7]}' for f in os.listdir(project_path_main) if isdir(join(project_path_main, f)) and f[:3] != '000']
full_path_list = [f for f in os.listdir(project_path_main) if isdir(join(project_path_main, f)) and f[:3] != '000']

project_path = 'S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/Work_Order_Storage/Construction'

def visitor_body(text, cm, tm, font_dict, font_size):
    x = tm[4]
    y = tm[5]
    text = text.replace('\n','')
    if x > 570 and 20 < y < 30: name.append(text)
    if x > 570 and 30 < y < 40: address.append(text)
    if x > 730 and 55 < y < 65: job_number.append(text)
    if x > 600 and 45 < y < 50: work_order.append(text)
    if x < 30:
        if 525 < y < 535: mechanic1_name.append(text)
        elif 540 < y < 550: mechanic2_name.append(text)
        elif 555 < y < 565: mechanic3_name.append(text)
        elif 570 < y < 580: mechanic4_name.append(text)
    if 165 < x < 175:
        if 525 < y < 535: mechanic1_reg.append(text)
        elif 540 < y < 550: mechanic2_reg.append(text)
        elif 555 < y < 565: mechanic3_reg.append(text)
        elif 570 < y < 580: mechanic4_reg.append(text)
    if 210 < x < 220:
        if 525 < y < 535: mechanic1_ot.append(text)
        elif 540 < y < 550: mechanic2_ot.append(text)
        elif 555 < y < 565: mechanic3_ot.append(text)
        elif 570 < y < 580: mechanic4_ot.append(text)
    if 255 < x < 265:
        if 525 < y < 535: mechanic1_dt.append(text)
        elif 540 < y < 550: mechanic2_dt.append(text)
        elif 555 < y < 565: mechanic3_dt.append(text)
        elif 570 < y < 580: mechanic4_dt.append(text)

files_list = [f for f in os.listdir(project_path) if isfile(join(project_path, f))]
files_list = iter(files_list)
for file_ in files_list:
    
    work_order = []
    job_number = []
    name = []; address = []
    mechanic1_name = []; mechanic2_name = []; mechanic3_name = []; mechanic4_name = []
    mechanic1_reg = []; mechanic2_reg = []; mechanic3_reg = []; mechanic4_reg = []
    mechanic1_ot = []; mechanic2_ot = []; mechanic3_ot = []; mechanic4_ot = []
    mechanic1_dt = []; mechanic2_dt = []; mechanic3_dt = []; mechanic4_dt = []

    with open(f'{project_path}/{file_}','rb') as f:
        try:
            pdf = PdfReader(f)
        except:
            error_count += 1
            print('Error', error_count, file_)
            next(files_list, None)
            continue
        meta_data = pdf.metadata        
        page_text = pdf.pages[0].extract_text(visitor_text=visitor_body)

    date = meta_data['/Title'][-10:]
    day = date[3:5]
    month = date[:2]
    year = date[-4:]

    address1 = address[0] if address else ''
    name1 = name[0] if name else ''
    job_number = job_number[0] if job_number else ''

    try:
        index = folder_list.index(job_number)

        with open (f'S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Construction/{full_path_list[index]}.json', 'r') as j:
            project_saved_data = json.load(j)

        work_order_number = work_order[0]

        if work_order_number not in project_saved_data['Visits']:

            path_temp = f'{project_path_main}/{full_path_list[index]}/Tech Service'
            print(path_temp)
            sub_dir = [f for f in os.listdir(path_temp) if isdir(join(path_temp, f))]
            if sub_dir:
                fuzz2 = process.extractOne('PMC Work Orders', sub_dir)
                sub_dir = fuzz2[0]
            else:
                sub_dir = 'PMC Work Orders'
            shutil.copy(f'{project_path}/{file_}',f'{path_temp}/{sub_dir}')

    except:
        print('Not in List', job_number)
        work_order_number = ''
 
    
    try:
        job_type = meta_data['/Subject']
    except:
        job_type = None


    project_data = {work_order_number:{'Month': month, 'Year': year, 'Day': day, 'Job#': job_number, 'Job_Type': job_type}}

    project_data[work_order_number].update({mechanic1_name[0]:{'Reg': float(mechanic1_reg[0]), 'OT': float(mechanic1_ot[0]), 'DT': float(mechanic1_dt[0])}})

    if mechanic2_name:
        project_data[work_order_number].update({mechanic2_name[0]:{'Reg': float(mechanic2_reg[0]), 'OT': float(mechanic2_ot[0]), 'DT': float(mechanic2_dt[0])}})

    if mechanic3_name:
        project_data[work_order_number].update({mechanic3_name[0]:{'Reg': float(mechanic3_reg[0]), 'OT': float(mechanic3_ot[0]), 'DT': float(mechanic3_dt[0])}})

    if mechanic4_name:
        project_data[work_order_number].update({mechanic4_name[0]:{'Reg': float(mechanic4_reg[0]), 'OT': float(mechanic4_ot[0]), 'DT': float(mechanic4_dt[0])}})

    #full_data.update(project_data)
