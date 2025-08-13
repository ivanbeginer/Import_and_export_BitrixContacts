from django import forms

from integration_utils.bitrix24.models import BitrixUserToken

user = BitrixUserToken.objects.filter(user__is_admin=True).first()
companies = ((company['ID'],company['TITLE']) for company in user.call_api_method('crm.company.list',params={'select': ['ID', 'TITLE']})['result'])
extensions = (('csv','csv'),('xlsx','xlsx'))
class ImportContact(forms.Form):
    file = forms.FileField(label='Выберите файл')

class ExportContacts(forms.Form):
    extension = forms.ChoiceField(label='В каком формате получить данные',choices=extensions)
    name = forms.CharField(label='Имя контакта')
    company = forms.ChoiceField(label='Компания',choices=companies)