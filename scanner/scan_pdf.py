import sys, os
from PyPDF2 import PdfReader, PdfMerger

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def pdf_scan(file_data):
    def visitor_body(text, cm, tm, font_dict, font_size):
        x = tm[4]
        y = tm[5]
        text = text.replace('\n','')
        #print(x, y, text)
        if x > 570 and 20 < y < 30: name_list.append(text)
        if x > 570 and 30 < y < 40: address_list.append(text)
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

    work_order = []; name_list = []
    job_number = []; address_list = []
    mechanic1_name = []; mechanic2_name = []; mechanic3_name = []; mechanic4_name = []
    mechanic1_reg = []; mechanic2_reg = []; mechanic3_reg = []; mechanic4_reg = []
    mechanic1_ot = []; mechanic2_ot = []; mechanic3_ot = []; mechanic4_ot = []
    mechanic1_dt = []; mechanic2_dt = []; mechanic3_dt = []; mechanic4_dt = []

    with open(resource_path('sample.pdf'), 'wb') as f:
        f.write(file_data)

    file_in = open(resource_path('sample.pdf'), 'rb')
    pdf = PdfReader(file_in)
    metadata = pdf.metadata
    pdf.pages[0].extract_text(visitor_text=visitor_body)

    file_in.close()
      

    if work_order:
        name = name_list[0] if name_list else ''
        address = address_list[0] if address_list else ''

        job_number1 = job_number[0] if job_number else ''

        dir_data = {'Name': name, 'Address': address, 'Job#': job_number1,'Years':{}}
      
        job_type = metadata['/Subject']
      
        date = metadata['/Title'][-10:]
        day = date[3:5]
        month = date[:2]
        year = date[-4:]

        dir_data['Years'].update({year: 0})

        visits = {'Date':f'{year}_{month}_{day}', 'Month': month, 'Year': year, 'Day': day, 'Job_Type': job_type,'Mechanics':{}}
            
        visits['Mechanics'].update({mechanic1_name[0]:{'Reg': float(mechanic1_reg[0]), 'OT': float(mechanic1_ot[0]), 'DT': float(mechanic1_dt[0])}})

        if mechanic2_name:
            visits['Mechanics'].update({mechanic2_name[0]:{'Reg': float(mechanic2_reg[0]), 'OT': float(mechanic2_ot[0]), 'DT': float(mechanic2_dt[0])}})

        if mechanic3_name:
            visits['Mechanics'].update({mechanic3_name[0]:{'Reg': float(mechanic3_reg[0]), 'OT': float(mechanic3_ot[0]), 'DT': float(mechanic3_dt[0])}})

        if mechanic4_name:
            visits['Mechanics'].update({mechanic4_name[0]:{'Reg': float(mechanic4_reg[0]), 'OT': float(mechanic4_ot[0]), 'DT': float(mechanic4_dt[0])}})

        return [dir_data, visits]
    

def update_meta_data(path: str, job_type: str):

    file_in = open(path, 'rb')
    pdf_reader = PdfReader(file_in)
    metadata = pdf_reader.metadata

    metadata.update({'/Subject': job_type})
    pdf_merger = PdfMerger()
    pdf_merger.append(file_in)
    pdf_merger.add_metadata(metadata)

    file_in.close()

    file_out = open(path, 'wb')
    pdf_merger.write(file_out)

    file_out.close()