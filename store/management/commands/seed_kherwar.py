from django.core.management.base import BaseCommand
from store.models import LunarMonth

MONTHS=[
('ᱢᱟᱜᱽ','MAG',False),('ᱯᱷᱟᱹᱜᱩᱱ','FAGUN',False),('ᱪᱟᱹᱛ','CHAIT',False),('ᱵᱟᱹᱭᱥᱟᱹᱠ','BAISAK',False),
('ᱡᱷᱮᱸᱴ','JHET',False),('ᱵᱟᱺᱰᱭᱟᱹ ᱡᱷᱮᱴ','BADYA JHET',True),('ᱟᱥᱟᲅ','ASAR',False),
('ᱥᱟᱱ','SAN',False),('ᱵᱷᱟᱫᱚᱨ','BHADOR',False),('ᱫᱟᱸᱥᱟᱸᱭ','DANSAY',False),
('ᱥᱚᱨᱦᱟᱭ','SARHAY',False),('ᱟᱸᱜᱷᱟᱲ','ANGHAR',False),('ᱯᱩᱥ','PUS',False)]

class Command(BaseCommand):
    help='Create/update the official 13 Santali month definitions.'
    def add_arguments(self, parser):
        parser.add_argument('--reset-names', action='store_true', help='Replace month names with the supplied official sequence.')
    def handle(self, *args, **opts):
        changed=0
        for i,(ol,en,extra) in enumerate(MONTHS,1):
            obj,created=LunarMonth.objects.get_or_create(order=i,defaults={'olchiki_name':ol,'english_name':en,'is_extra':extra,'active':True})
            if opts['reset_names']:
                obj.olchiki_name=ol; obj.english_name=en; obj.is_extra=extra; obj.active=True; obj.save(); changed+=1
            elif created:
                changed+=1
        self.stdout.write(self.style.SUCCESS(f'Kherwar months ready: 13 definitions ({changed} created/updated).'))
