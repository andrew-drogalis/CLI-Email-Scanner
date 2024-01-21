from __future__ import print_function
import sys, os, os.path, json, base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from os.path import isdir, join, isfile
from scanner.scan_pdf import pdf_scan, update_meta_data
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def folder_job_number(type_: str):

    init_path = 'S:/PIERPONT MAINTENANCE & SERVICE/SERVICE CONTRACTS & PROPOSALS'
    # Maintenance Folders
    if type_ == 'M':
        scanned_jobs = {folder[:6]:f'{init_path}/{folder}' for folder in os.listdir(init_path) if isdir(join(init_path, folder)) and folder[:3] != '000' and folder[3:6] == '-MS'}

    if type_ == 'C':
        init_path = 'P:'
        # Construction Folder
        scanned_jobs = {}
        year_folder_list = [f for f in os.listdir(init_path) if isdir(join(init_path, f)) and f[:8] == 'Projects' and int(f[-4:]) >= 2021]

        for year in year_folder_list:

            for f in os.listdir(f'{init_path}/{year}'):
                
                if isdir(join(f'{init_path}/{year}', f)) and f[:3] != '000':

                    if f[3] == '-' or f[3] == '_':
                        name = f'{f[:3]}-{f[5:7]}'
                    else:
                        name = f'{f[:3]}-{f[3]}{f[6:8]}'
                    scanned_jobs.update({name:f'{init_path}/{year}/{f}'})

    return scanned_jobs

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    time_stamp_new = int(datetime.now().timestamp())

    with open('S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/email_timestamp.json', 'r') as j:
        time_data = json.load(j)

    time_stamp = time_data['Email']
 
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    if os.path.exists(resource_path('data/token.json')):
        creds = Credentials.from_authorized_user_file(resource_path('data/token.json'), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                resource_path('data/credentials.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(resource_path('data/token.json'), 'w') as token:
            token.write(creds.to_json())

    
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
       
        results = service.users().messages().list(userId='me', q=f'after:{time_stamp}', maxResults=500, labelIds=['INBOX']).execute()
        messages = results.get('messages')
        time_data['Email'] = time_stamp_new
        messages = [] if not messages else messages

        # iterate through all the messages
        for msg in messages:

            # Get the message from its id
            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            
            # Get value of 'payload' from dictionary 'txt'
            payload = txt['payload']
            headers = payload['headers']

            # Look for Subject and Sender Email in the headers
            subject = [d['value'] for d in headers if d['name'] == 'Subject'][0]
            sender = [d['value'] for d in headers if d['name'] == 'From'][0]

            subject_text = subject.split('_')
        
            if len(subject_text) > 1:
                work_order = subject_text[1][:11]
                if work_order == 'Work Order#' and 'parts' in [*payload.keys()]:
                    # Save Attachment
                    for part in payload['parts']:
                        if part['filename']:
                            if 'data' in part['body']:
                                data = part['body']['data']
                            else:
                                att_id = part['body']['attachmentId']
                                att = service.users().messages().attachments().get(userId='me', messageId=msg['id'],id=att_id).execute()
                                data = att['data']
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                            attachment_type = part['filename'].split('.')
                            try:
                                confirm_date = int(attachment_type[-2].split('_')[-1] or 0)
                            except:
                                confirm_date = 0

                            if attachment_type[-1] == 'pdf' and confirm_date >= 2021:
                                extracted_data = pdf_scan(file_data=file_data)

                                visits = extracted_data[1]; dir_data = extracted_data[0]

                                job_type = visits['Job_Type']
                                job_number = dir_data['Job#']

                                print("From: ", sender)
                                print("Subject: ", subject)
                                print("Body: ", txt['snippet'])
                                print('\n')
                                update_metadata = False
                                discard = False

                                if job_type == 'Manual Entry':
                                    while True:
                                        selected = input('This Work Order is a Manual Entry. Please Choose from (1) of the following:\n1. Discard Email, 2. Maintenance, 3. Emergency Service, 4. Proposal, 5. Construction\n\nInput Selection #: ')
                                        selected = selected.replace('#','').replace('.','')
                                        if selected in ['1', '2', '3', '4', '5']:
                                            break
                                        else:
                                            print('Not in Options Number Range. Please Try Again.')
                                    
                                    if selected != '1':
                                        job_type = 'Maintenance' if selected == '2' else 'Emergency Service' if selected == '3' else 'Proposal' if selected == '4' else 'Construction'
                                        update_metadata = True

                                if job_type != 'Manual Entry':
                                    
                                    if job_type in ['Maintenance', 'Emergency Service', 'Proposal']:
                                        path_work_order_main = f"S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/Work_Order_Storage/Maintenance"
                                        if not job_number:
                                            job_number = input('No Job Number. Please Enter Job Number in the format "001-MS" for Maintenance.\n\nInput Job #: ').upper()

                                        while True:
                                            folders = folder_job_number(type_='M')
                                            folder_type = 'Maintenance'
                                            if job_number in [*folders.keys()]:
                                                selected = input(f'Job Number Matched with {job_number}. Please Type "Y" to confirm or "N" to change. \n\nInput: ').upper()
                                                if selected == 'Y':
                                                    break
                                                elif selected == 'N':
                                                    job_number = input('Please Enter New Job Number in the format "001-MS" for Maintenance.\n\nInput Job #: ').upper()
                                            
                                            else:
                                                selected = input(f'Job Number {job_number} is not in maintenance folder. Please Type "Y" after folder added to maintenance or "N" to change job number. (Type "Skip" to discard) \n\nInput: ').upper()
                                                if selected == 'N':
                                                    job_number = input('Please Enter New Job Number in the format "001-MS" for Maintenance.\n\nInput Job #: ').upper()
                                                elif selected == 'SKIP':
                                                    discard = True; break

                                    elif job_type == 'Construction':
                                        path_work_order_main = f"S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/Work_Order_Storage/Construction"
                                        if not job_number:
                                            job_number = input('No Job Number. Please Enter Job Number in the format "001-23" for Construction.\n\nInput Job #: ').upper()
                                        try:
                                            job_number_year = int(job_number[-2:] or 0)
                                        except:
                                            job_number_year = 0

                                        while True:
                                            folders = folder_job_number(type_='C')
                                            folder_type = 'Construction'
                                            if job_number in [*folders.keys()]:
                                                selected = input(f'Job Number Matched with {job_number}. Please Type "Y" to confirm or "N" to change. \n\nInput: ').upper()
                                                if selected == 'Y':
                                                    break
                                                elif selected == 'N':
                                                    job_number = input('Please Enter New Job Number in the format "001-23" for Construction.\n\nInput Job #: ').upper()
                                            elif job_number_year < 21:
                                                input('Project is older than 2021. Please Place Manually.\nPress Any Key to Continue...')
                                                discard = True; break
                                            else:
                                                selected = input(f'Job Number {job_number} is not in construction folder. Please Type "Y" after folder added to construction or "N" to change job number. (Type "Skip" to discard) \n\nInput: ').upper()
                                                if selected == 'N':
                                                    job_number = input('Please Enter New Job Number in the format "001-23" for Construction.\n\nInput Job #: ').upper()
                                                elif selected == 'SKIP':
                                                    discard = True; break
                                   
                                    if not discard:
                                        # Place in Main Storage
                                        if not os.path.exists(f"{path_work_order_main}/{part['filename']}"):
                                            with open(f"{path_work_order_main}/{part['filename']}", 'wb') as f:
                                                f.write(file_data)

                                            if update_metadata:
                                                update_meta_data(path=f"{path_work_order_main}/{part['filename']}",job_type=job_type)

                                        if folder_type == 'Maintenance':
                                            path_storage = f"S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Maintenance"
                                            job_folder_path = folders[job_number]
                                            year = visits['Year']
                                            if not isdir(f"{job_folder_path}/Work Orders/{year}") and not isfile(f"{job_folder_path}/Work Orders/{year}"):
                                                os.mkdir(f"{job_folder_path}/Work Orders/{year}")
                                            elif not isdir(f"{job_folder_path}/Work Orders/{year}") and isfile(f"{job_folder_path}/Work Orders/{year}"):
                                                print(f'Warning Corrupt Folder at {job_folder_path}/Work Orders/{year}\n\n')
                                                print('Step 1: Navigate to folder above and delete corrupted files.')
                                                print('Step 2: Exit this application')
                                                print('Step 3: Take note of this corruption location and remind Andrew to do manual restore.')
                                                input('Press Any Key to Exit... ')
                                                exit()
                                            
                                            # Place in Maintenance Storage
                                            if not os.path.exists(f"{job_folder_path}/Work Orders/{year}/{part['filename']}"):
                                                with open(f"{job_folder_path}/Work Orders/{year}/{part['filename']}", 'wb') as f:
                                                    f.write(file_data)

                                                if update_metadata:
                                                    update_meta_data(path=f"{job_folder_path}/Work Orders/{year}/{part['filename']}",job_type=job_type)

                                        elif folder_type == 'Construction':
                                            path_storage= f"S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/File_System_Scans/Construction"
                                            job_folder_path = f'{folders[job_number]}/Tech Service'
                            
                                            for sub_dir in os.listdir(job_folder_path):
                                                if isdir(join(job_folder_path, sub_dir)) and ('PMC' in sub_dir or 'pmc' in sub_dir):
                                                    final_directory = sub_dir; break
                                            else:
                                                for sub_dir in os.listdir(job_folder_path):
                                                    if isfile(join(job_folder_path, sub_dir)) and ('PMC' in sub_dir or 'pmc' in sub_dir):
                                                        print(f'Warning Corrupt Folder at {job_folder_path}/{sub_dir}\n\n')
                                                        print('Step 1: Navigate to folder above and delete corrupted files.')
                                                        print('Step 2: Exit this application')
                                                        print('Step 3: Take note of this corruption location and remind Andrew to do manual restore.')
                                                        input('Press Any Key to Exit... ')
                                                        exit()
                                                else:
                                                    os.mkdir(f"{job_folder_path}/PMC Work Orders")
                                                    final_directory = 'PMC Work Orders'
                                            
                                            # Place in Construction Storage
                                            if not os.path.exists(f"{job_folder_path}/{final_directory}/{part['filename']}"):
                                                with open(f"{job_folder_path}/{final_directory}/{part['filename']}", 'wb') as f:
                                                    f.write(file_data)

                                                if update_metadata:
                                                    update_meta_data(path=f"{job_folder_path}/{final_directory}/{part['filename']}",job_type=job_type)

                                        # Update Project File Scan JSON
                                        job = folders[job_number].split('/')[-1]
                                        try:
                                            with open(f'{path_storage}/{job}.json', 'r') as j:
                                                job_data = json.load(j)

                                            Previous_Update = True
                                            if visits not in job_data['Visits']:
                                                Previous_Update = False
                                                job_data['Visits'].append(visits)
                                                job_data['Years'].update(dir_data['Years'])
                                        except:
                                            Previous_Update = False
                                            dir_data.update({'Visits':[visits]})
                                            job_data = {**dir_data}

                                        if not Previous_Update:
                                            with open(f'{path_storage}/{job}.json', 'w') as j:
                                                json.dump(job_data, j)

                                            # ----------------------------------
                                            # Update Cumulative Scan JSON
                                            name = f'{path_storage}/full_{folder_type.lower()}.json'
                                            
                                            if job_type in ['Maintenance', 'Emergency Service', 'Construction']:
                                                try:
                                                    with open(name, 'r') as j:
                                                        job_data = json.load(j)
                                                        
                                                    job_data['Years'].update(dir_data['Years'])
                                                    job_data['Visits'][job_type].append(visits)
                                                    
                                                    with open(name, 'w') as j:
                                                        json.dump(job_data, j)

                                                except:
                                                    print('Full System JSON File Missing. Perform Full System Scan.')


                                #print('TEMP DATA: -> ',visits, dir_data)
                                print('')
                            
        
        with open('S:/PIERPONT MAINTENANCE & SERVICE/Data_Storage/email_timestamp.json', 'w') as j:
            json.dump(time_data, j)
                
    except HttpError as error:
        print(f'HTTP Gmail Error {error}')



       