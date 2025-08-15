from django.shortcuts import render
from contacts.extensions import get_file_handler
from contacts.forms import ImportContact, ExportContacts
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from contacts.extensions import file_handler_dict

def create_filter(data,contact_fields):
    filter = {}
    for k, v in data.items():
        if k in contact_fields and data.get(k):
            filter[k] = v
    return filter



@main_auth(on_cookies=True)
def import_contacts(request):
    user = request.bitrix_user_token
    form = ImportContact(request.POST,request.FILES)
    companies = user.call_list_method('crm.company.list', fields={'select': ['ID', 'TITLE']})
    contacts = user.call_list_method('crm.contact.list',fields={'select': ['ID', 'NAME', 'LAST_NAME', 'EMAIL', 'COMPANY_ID', 'PHONE']})
    print(len(contacts))
    phones = [contact_from_contacts['PHONE'][0]['VALUE'] for contact_from_contacts in contacts]
    phones_and_ids = {contact['PHONE'][0]['VALUE']:contact['ID'] for contact in contacts}
    print(phones_and_ids)
    for_batch_add = []
    for_batch_update = []
    if request.method=='POST':
        if form.is_valid():
            data = form.cleaned_data
            reader = get_file_handler(data['file']).read(data['file'])
            print(reader)
            print(len(contacts))
            for row in reader:
                row['COMPANY_ID']=[company['ID'] for company in companies if company['TITLE']==row['COMPANY_NAME']]
            print(reader)
            for index,contact in enumerate(reader):
                if '+'+str(contact['PHONE']) in phones:
                    for_batch_update.append((f'contact_{index}','crm.contact.update',{'id':f'{phones_and_ids['+'+str(contact['PHONE'])]}','fields':{
                    'NAME':contact['NAME'],
                    'LAST_NAME':contact['LAST_NAME'],
                    'EMAIL':[{'VALUE':contact['EMAIL']}],
                    'COMPANY_ID':contact['COMPANY_ID'][0]
                }}))
                else:
                    for_batch_add.append((f'contact_{index}','crm.contact.add',{'fields':{
                        'NAME':contact['NAME'],
                        'LAST_NAME':contact['LAST_NAME'],
                        'EMAIL':[{'VALUE':contact['EMAIL']}],
                        'COMPANY_ID':contact['COMPANY_ID'][0],
                        'PHONE':[{'VALUE':'+'+str(contact['PHONE'])}]
                    }}))
            print(for_batch_update)
            print(for_batch_add)
            print(len(for_batch_update))
            batch_add = user.batch_api_call(methods=for_batch_add)
            batch_update = user.batch_api_call(methods=for_batch_update)
            return render(request,'success.html')
    return render(request,'import.html',locals())


@main_auth(on_cookies=True)
def export_contacts(request):
    user = request.bitrix_user_token
    form = ExportContacts(request.POST)
    companies = user.call_list_method('crm.company.list', fields={'select': ['ID', 'TITLE']})
    contact_fields = list(user.call_api_method('crm.contact.fields')['result'].keys())

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data

            res = user.call_list_method('crm.contact.list',
                                       fields={'filter':create_filter(data,contact_fields),
                                               'select': ['ID', 'NAME', 'LAST_NAME', 'EMAIL', 'COMPANY_ID','PHONE']})
            for contact in res:
                contact['EMAIL']=contact['EMAIL'][0]['VALUE']
                contact['PHONE']=contact['PHONE'][0]['VALUE']
                contact['COMPANY_NAME']=[company['TITLE'] for company in companies if contact['COMPANY_ID']==company['ID']][0]
                del contact['COMPANY_ID']


            writer = file_handler_dict.get(data['extension'])().write(res,data['title']+f'.{data['extension']}')
            print(writer)
            return writer

    return render(request,'export.html',locals())