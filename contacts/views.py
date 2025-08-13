from django.shortcuts import render
from contacts.extensions import get_file_handler
from contacts.forms import ImportContact, ExportContacts
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from contacts.extensions import file_handler_dict


@main_auth(on_cookies=True)
def import_contacts(request):
    user = request.bitrix_user_token
    form = ImportContact(request.POST,request.FILES)
    context = []
    res_context = []
    companies = user.call_api_method('crm.company.list', params={'select': ['ID', 'TITLE']})['result']
    result_struct = {}
    for_batch = []
    if request.method=='POST':
        if form.is_valid():
            data = form.cleaned_data
            reader = get_file_handler(data['file']).read(data['file']).to_dict('records')
            print(reader)
            for row in reader:
                row['COMPANY_ID']=[company['ID'] for company in companies if company['TITLE']==row['COMPANY_NAME']]
                context.append(row)
    for index,contact in enumerate(context):
        for_batch.append((f'contact_{index}','crm.contact.add',{'fields':{
            'NAME':contact['NAME'],
            'LAST_NAME':contact['LAST_NAME'],
            'EMAIL':[{'VALUE':contact['EMAIL']}],
            'COMPANY_ID':contact['COMPANY_ID'][0]
        }}))
    batch = user.batch_api_call(methods=for_batch)
    print(batch)
    return render(request,'import.html',locals())


@main_auth(on_cookies=True)
def export_contacts(request):
    user = request.bitrix_user_token
    form = ExportContacts(request.GET)
    if request.method == 'GET':
        if form.is_valid():
            data = form.cleaned_data
            res = user.call_api_method('crm.contact.list',params={'filter':{'NAME':data['name'],'COMPANY':data['company']},'select':['ID','NAME','LAST_NAME','EMAIL','COMPANY_ID','EXPORT']})['result']
            print(res)

            writer = file_handler_dict.get(data['extension'])().write(res)
            print(writer)


    return render(request,'export.html',locals())