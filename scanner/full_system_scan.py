import json, os
from datetime import datetime
from os.path import isfile, join, isdir
from PyPDF2 import PdfReader

class FullSystemScan():

    def __init__(self, bypass = False):
        self.error_count = 0
        with open('S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/email_timestamp.json', 'r') as j:
            time_data = json.load(j)

        if bypass or datetime.now().timestamp() - time_data['Full_Scan'] > 604_800:
            print('\n~ FULL SYSTEM SCAN ~ \n\nApproximate Time to Completion: 15 Minutes \n\nProcessing...')
            self.maintenance_projects()
            self.construction_projects()
            self.cumulative_maintenance()
            self.cumulative_construction()
            time_data['Full_Scan'] = int(datetime.now().timestamp())
            with open('S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/email_timestamp.json', 'w') as j:
                json.dump(time_data, j)
            print('\n100% Completed.\n')

    def maintenance_projects(self):
        project_path = 'S:/PIERPONT MAINTENANCE & SERVICE/SERVICE CONTRACTS & PROPOSALS'
        folder_list = [f for f in os.listdir(project_path) if isdir(join(project_path, f)) and f[:3] != '000' and f[3:6] == '-MS']

        for folder in folder_list:

            work_order_path = f'{project_path}/{folder}/Work Orders'
            self.dir_data = {'Visits':[],'Years':{}}
            name_data_temp = {}
            
            for sub_dir in os.listdir(work_order_path):
                
                try:
                    sub_int = int(sub_dir[:4])
                except:
                    sub_int = 0
                
                if isdir(join(work_order_path, sub_dir)) and sub_int >= 2022:
        
                    for file_ in os.listdir(f'{work_order_path}/{sub_dir}'):

                        if isfile(join(f'{work_order_path}/{sub_dir}', file_)) and file_[-3:] == 'pdf':

                            name_data = self.work_order_processing(path=f'{work_order_path}/{sub_dir}/{file_}')
                            if name_data:
                                name_data_temp = {**name_data}

            self.dir_data.update(name_data_temp)

            with open(f'S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Maintenance/{folder}.json', 'w') as j:
                json.dump(self.dir_data, j)

    def construction_projects(self):
        init_path = 'P:/'
        year_folder_list = [f for f in os.listdir(init_path) if isdir(join(init_path, f)) and f[:8] == 'Projects' and int(f[-4:]) >= 2021]

        for year in year_folder_list:

            for project in os.listdir(f'{init_path}/{year}'):
                        
                if isdir(join(f'{init_path}/{year}', project)) and project[:3] != '000':

                    work_order_path = f'{init_path}/{year}/{project}/Tech Service'
                    self.dir_data = {'Visits':[],'Years':{}}
                    name_data_temp = {}

                    check_path = os.path.isdir(work_order_path)
                    # If folder doesn't exist, then create it.
                    if not check_path:
                        os.makedirs(work_order_path)

                    for sub_dir in os.listdir(work_order_path):

                        if isdir(join(work_order_path, sub_dir)) and ('PMC' in sub_dir or 'pmc' in sub_dir):
                            
                            for file_ in os.listdir(f'{work_order_path}/{sub_dir}'):

                                if isfile(join(f'{work_order_path}/{sub_dir}', file_)) and file_[-3:] == 'pdf':

                                    name_data = self.work_order_processing(path=f'{work_order_path}/{sub_dir}/{file_}')
                                    if name_data:
                                        name_data_temp = {**name_data}
                                    
                    self.dir_data.update(name_data_temp)

                    with open(f'S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Construction/{project}.json', 'w') as j:
                        json.dump(self.dir_data, j)

    def cumulative_maintenance(self):
   
        project_path = 'S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/Work_Order_Storage/Maintenance'

        self.dir_data = {'Name': 'Full Maintenance', 'Address': 'Full Maintenance', 'Job#': 'Full Maintenance', 'Years':{}, 'Visits':[]}

        maintenance_visits_list = []; emergency_visits_list = []
        files_list = [f for f in os.listdir(project_path) if isfile(join(project_path, f))]
        files_list = iter(files_list)
        for file_ in files_list:
            
            self.work_order_processing(path=f'{project_path}/{file_}')

            if self.dir_data['Visits'][-1]['Job_Type'] == 'Maintenance':
                maintenance_visits_list.append(self.dir_data['Visits'][-1])

            elif self.dir_data['Visits'][-1]['Job_Type'] == 'Emergency Service':
                emergency_visits_list.append(self.dir_data['Visits'][-1])

        self.dir_data.update({'Visits':{'Maintenance':maintenance_visits_list,'Emergency Service':emergency_visits_list}})

        with open('S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Maintenance/full_maintenance.json', 'w') as j:
            json.dump(self.dir_data, j)

    def cumulative_construction(self):

        project_path = 'S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/Work_Order_Storage/Construction'

        self.dir_data = {'Name': 'Full Construction', 'Address': 'Full Construction', 'Job#': 'Full Construction', 'Years':{}, 'Visits':[]}

        files_list = [f for f in os.listdir(project_path) if isfile(join(project_path, f))]
        files_list = iter(files_list)
        for file_ in files_list:
            
            self.work_order_processing(path=f'{project_path}/{file_}')   
            
        self.dir_data.update({'Visits':{'Construction':self.dir_data['Visits']}})

        with open('S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Construction/full_construction.json', 'w') as j:
            json.dump(self.dir_data, j)


    # -------------------------------------------

    def work_order_processing(self, path: str):

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

        with open(path,'rb') as f:
            try:
                pdf = PdfReader(f)
                meta_data = pdf.metadata        
                pdf.pages[0].extract_text(visitor_text=visitor_body)
            except:
                self.error_count += 1
                print(f'Error #{self.error_count} at location: {path}')

        if work_order:
            name = name_list[0] if name_list else ''
            address = address_list[0] if address_list else ''

            job_number1 = job_number[0] if job_number else ''
            try:
                job_type = meta_data['/Subject']
            except:
                job_type = None

            date = meta_data['/Title'][-10:]
            day = date[3:5]
            month = date[:2]
            year = date[-4:]

            self.dir_data['Years'].update({year: 0})

            self.dir_data['Visits'].append({'Date':f'{year}_{month}_{day}', 'Month': month, 'Year': year, 'Day': day, 'Job_Type': job_type,'Mechanics':{}})
                
            self.dir_data['Visits'][-1]['Mechanics'].update({mechanic1_name[0]:{'Reg': float(mechanic1_reg[0]), 'OT': float(mechanic1_ot[0]), 'DT': float(mechanic1_dt[0])}})

            if mechanic2_name:
                self.dir_data['Visits'][-1]['Mechanics'].update({mechanic2_name[0]:{'Reg': float(mechanic2_reg[0]), 'OT': float(mechanic2_ot[0]), 'DT': float(mechanic2_dt[0])}})

            if mechanic3_name:
                self.dir_data['Visits'][-1]['Mechanics'].update({mechanic3_name[0]:{'Reg': float(mechanic3_reg[0]), 'OT': float(mechanic3_ot[0]), 'DT': float(mechanic3_dt[0])}})

            if mechanic4_name:
                self.dir_data['Visits'][-1]['Mechanics'].update({mechanic4_name[0]:{'Reg': float(mechanic4_reg[0]), 'OT': float(mechanic4_ot[0]), 'DT': float(mechanic4_dt[0])}})

            return {'Name': name, 'Address': address, 'Job#': job_number1}
        