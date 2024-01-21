from PyPDF2 import PdfReader, PdfMerger

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


update_meta_data(path="P:/Projects_2022/100_S22_BXP Boston Properties_767 5th Ave_BXP Boston Properties/Tech Service/PMC Work Orders/BOSTON PROPERTIES_Work Order#0001594_07_13_2022.pdf", job_type='Construction')