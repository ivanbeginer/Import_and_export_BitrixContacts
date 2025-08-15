from django import forms

from integration_utils.bitrix24.models import BitrixUserToken

user = BitrixUserToken.objects.filter(user__is_admin=True).first()
companies = [(company['ID'],company['TITLE']) for company in user.call_api_method('crm.company.list',params={'select': ['ID', 'TITLE']})['result']]
companies.append(('','Все компании'))
# print(companies)
#res_companies = ((company['ID'],company['TITLE']) for company in companies)
extensions = (('csv','csv'),('xlsx','xlsx'))
class ImportContact(forms.Form):
    file = forms.FileField(label='Выберите файл')

class ExportContacts(forms.Form):
    extension = forms.ChoiceField(label='В каком формате получить данные',choices=extensions,required=False)
    title = forms.CharField(label='Название файла для экспорта', required=False, empty_value='export')
    NAME = forms.CharField(label='Имя контакта',required=False,empty_value='')
    COMPANY_ID = forms.ChoiceField(label='Компания',choices=companies,required=False)
