import os ,django
from django.core.management import call_command
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE','project.settings')
django.setup()
def export_model_to_fixture(model):
    app_label=model._meta.app_label
    model_name=model._meta.model_name
    fixture_path=os.path.join('backup',f'{app_label}.{model_name}.json')
    with open(fixture_path,'w',encoding='utf-8') as f:
            call_command('dumpdata', f'{app_label}.{model_name}',stdout=f)


def export_all_models():
    export_directory= 'backup'
    os.makedirs(export_directory,exist_ok=True)
    all_models=apps.get_models()    
    for model in all_models:
            export_model_to_fixture(model)
    
if __name__=='__main__':
    export_all_models()