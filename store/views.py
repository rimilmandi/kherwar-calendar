import csv
import io
import json
import os
import uuid
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from .models import (
    LunarMonth,
    NewMoon,
    HistoricalDate,
    LunarEvent,
    SolarEvent,
    Advertisement,
    SiteSetting,
)


# ============================================================
# ১. DEFAULT SANTALI MONTHS
# ============================================================

MONTH_DEFAULTS = [
    ('ᱢᱟᱜᱽ', 'MAG', False),
    ('ᱯᱷᱟᱹᱜᱩᱱ', 'FAGUN', False),
    ('ᱪᱟᱹᱛ', 'CHAIT', False),
    ('ᱵᱟᱹᱭᱥᱟᱹᱠ', 'BAISAK', False),
    ('ᱡᱷᱮᱸᱴ', 'JHET', False),
    ('ᱵᱟᱺᱰᱭᱟᱹ ᱡᱷᱮᱴ', 'BADYA JHET', True),
    ('ᱟᱥᱟᱲ', 'ASAR', False),
    ('ᱥᱟᱱ', 'SAN', False),
    ('ᱵᱷᱟᱫᱚᱨ', 'BHADOR', False),
    ('ᱫᱟᱸᱥᱟᱸᱭ', 'DANSAY', False),
    ('ᱥᱚᱨᱦᱟᱭ', 'SARHAY', False),
    ('ᱟᱸᱜᱷᱟᱲ', 'ANGHAR', False),
    ('ᱯᱩᱥ', 'PUS', False),
]


# ============================================================
# ২. MONTH SETUP
# ============================================================

def ensure_months():
    for i, (olchiki, english, extra) in enumerate(MONTH_DEFAULTS, 1):
        LunarMonth.objects.get_or_create(
            order=i,
            defaults={
                'olchiki_name': olchiki,
                'english_name': english,
                'is_extra': extra,
                'active': True,
            }
        )


# ============================================================
# ৩. JSON SERIALIZERS
# ============================================================

def month_json(m):
    return {
        'id': m.id,
        'order': m.order,
        'olchiki_name': m.olchiki_name,
        'english_name': m.english_name,
        'is_extra': m.is_extra,
    }


def hist_json(x):
    return {
        'id': x.id,
        'date': x.gregorian.isoformat(),
        'bDay': x.bengali_day,
        'bMonth': x.bengali_month,
        'bYear': x.bengali_year,
        'sDay': x.santali_day,
        'sMonth': x.santali_month,
        'sYear': x.santali_year,
        'note': x.note,
    }


# ------------------------------------------------------------
# Lunar Event JSON
# এখন day-এর পরিবর্তে day_from এবং day_to
# ------------------------------------------------------------

def event_json(x):
    return {
        'id': x.id,
        'month': x.month_order,
        'day_from': x.day_from,
        'day_to': x.day_to,
        'title': x.title,
        'description': x.description,
        'image': x.image,
        'label': x.label,
    }


def solar_json(x):
    return {
        'id': x.id,
        'date': x.date.isoformat(),
        'title': x.title,
        'description': x.short_description,
        'details': x.details,
        'image': x.image,
    }


def ad_json(x):
    return {
        'id': x.id,
        'slot': x.slot,
        'business_name': x.business_name,
        'image': x.image,
        'target_url': x.target_url,
        'start_date': x.start_date.isoformat() if x.start_date else None,
        'end_date': x.end_date.isoformat() if x.end_date else None,
        'priority': x.priority,
    }


# ============================================================
# ৪. STAFF CHECK
# ============================================================

def staff_required(request):
    return request.user.is_authenticated and request.user.is_staff


# ============================================================
# ৫. IMAGE UPLOAD
# ============================================================

@login_required
@require_http_methods(['POST'])
def upload_image(request):

    if not request.user.is_staff:
        return JsonResponse(
            {'error': 'Admin login required'},
            status=403
        )

    f = request.FILES.get('image')

    if not f:
        return JsonResponse(
            {'error': 'Image file required'},
            status=400
        )

    allowed = {
        '.jpg',
        '.jpeg',
        '.png',
        '.webp',
        '.gif',
        '.svg',
        '.bmp',
        '.avif',
    }

    ext = os.path.splitext(f.name.lower())[1]

    if ext not in allowed:
        return JsonResponse(
            {
                'error': (
                    'Allowed image types: '
                    'JPG, JPEG, PNG, WEBP, GIF, SVG, BMP, AVIF'
                )
            },
            status=400
        )

    if f.size > 10 * 1024 * 1024:
        return JsonResponse(
            {
                'error': 'Image must be 10 MB or smaller'
            },
            status=400
        )

    try:

        upload_dir = settings.MEDIA_ROOT / 'calendar_images'
        upload_dir.mkdir(parents=True, exist_ok=True)

        fs = FileSystemStorage(
            location=upload_dir,
            base_url=settings.MEDIA_URL + 'calendar_images/'
        )

        safe_name = f"{uuid.uuid4().hex}{ext}"

        saved = fs.save(safe_name, f)

        return JsonResponse(
            {
                'ok': True,
                'url': fs.url(saved),
                'name': saved,
            }
        )

    except Exception as e:

        return JsonResponse(
            {
                'error': f'Image upload failed: {str(e)}'
            },
            status=500
        )


# ============================================================
# ৬. ADMIN PANEL
# ============================================================

def admin_panel(request):

    if not staff_required(request):
        return redirect(
            f'{reverse("login")}?next={request.path}'
        )

    return render(request, 'admin.html')


# ============================================================
# ৭. BOOTSTRAP
# ============================================================

@require_GET
def bootstrap(request):

    ensure_months()

    return JsonResponse(
        {
            'months': [
                month_json(x)
                for x in LunarMonth.objects.filter(active=True)
            ],

            'history': [
                hist_json(x)
                for x in HistoricalDate.objects.all()
            ],

            'newMoons': [
                {
                    'id': x.id,
                    'date': x.date.isoformat(),
                    'lunar_year': x.lunar_year,
                    'month_order': x.month_order,
                    'note': x.note,
                }
                for x in NewMoon.objects.all()
            ],

            'events': [
                event_json(x)
                for x in LunarEvent.objects.filter(active=True)
            ],

            'solarEvents': [
                solar_json(x)
                for x in SolarEvent.objects.filter(active=True)
            ],

            'ads': [
                ad_json(x)
                for x in Advertisement.objects.filter(active=True)
            ],

            'settings': {
                x.key: x.value
                for x in SiteSetting.objects.all()
            },
        }
    )


# ============================================================
# ৮. CALENDAR MONTH API
# ============================================================

@require_GET
def calendar_month(request):

    try:
        y = int(request.GET['year'])
        m = int(request.GET['month'])

    except (KeyError, ValueError):

        return JsonResponse(
            {
                'error': 'year and month required'
            },
            status=400
        )

    start = date(y, m, 1)

    end = (
        date(y + 1, 1, 1)
        if m == 12
        else date(y, m + 1, 1)
    )

    return JsonResponse(
        {
            'history': {
                x.gregorian.isoformat(): hist_json(x)
                for x in HistoricalDate.objects.filter(
                    gregorian__gte=start,
                    gregorian__lt=end
                )
            },

            'newMoons': [
                {
                    'id': x.id,
                    'date': x.date.isoformat(),
                    'lunar_year': x.lunar_year,
                    'month_order': x.month_order,
                }
                for x in NewMoon.objects.filter(
                    date__gte=start - timedelta(days=40),
                    date__lt=end + timedelta(days=40)
                )
            ],

            'events': [
                event_json(x)
                for x in LunarEvent.objects.filter(active=True)
            ],

            'solarEvents': [
                solar_json(x)
                for x in SolarEvent.objects.filter(
                    active=True,
                    date__gte=start,
                    date__lt=end
                )
            ],

            'ads': [
                ad_json(x)
                for x in Advertisement.objects.filter(active=True)
            ],
        }
    )


# ============================================================
# ৯. MAIN DATA API
# ============================================================

@login_required
@require_http_methods(['POST', 'PUT', 'DELETE'])
def data_api(request, kind):

    if not request.user.is_staff:
        return JsonResponse(
            {'error': 'Admin login required'},
            status=403
        )

    try:
        body = json.loads(request.body or '{}')

    except json.JSONDecodeError:

        return JsonResponse(
            {'error': 'Invalid JSON'},
            status=400
        )

    model_map = {
        'month': LunarMonth,
        'moon': NewMoon,
        'history': HistoricalDate,
        'event': LunarEvent,
        'solar': SolarEvent,
        'ad': Advertisement,
        'setting': SiteSetting,
    }

    Model = model_map.get(kind)

    if not Model:
        return JsonResponse(
            {'error': 'Unknown resource'},
            status=404
        )

    obj = (
        Model.objects.filter(pk=body.get('id')).first()
        if body.get('id')
        else None
    )

    # ========================================================
    # DELETE
    # ========================================================

    if request.method == 'DELETE':

        if not obj:
            return JsonResponse(
                {'error': 'Not found'},
                status=404
            )

        obj.delete()

        return JsonResponse(
            {'ok': True}
        )

    # ========================================================
    # MONTH
    # ========================================================

    if kind == 'month':

        obj = obj or Model()

        obj.order = int(body['order'])

        obj.olchiki_name = body.get(
            'olchiki_name',
            ''
        )

        obj.english_name = body.get(
            'english_name',
            ''
        )

        obj.is_extra = bool(
            body.get('is_extra')
        )

        obj.active = True

    # ========================================================
    # NEW MOON
    # ========================================================

    elif kind == 'moon':

        obj = obj or Model()

        obj.date = body['date']

        obj.lunar_year = (
            body.get('lunar_year')
            or None
        )

        obj.month_order = (
            body.get('month_order')
            or None
        )

        obj.note = body.get(
            'note',
            ''
        )

    # ========================================================
    # HISTORICAL DATE
    # ========================================================

    elif kind == 'history':

        obj = obj or Model()

        obj.gregorian = body['date']

        obj.bengali_day = (
            body.get('bDay')
            or None
        )

        obj.bengali_month = body.get(
            'bMonth',
            ''
        )

        obj.bengali_year = (
            body.get('bYear')
            or None
        )

        obj.santali_day = (
            body.get('sDay')
            or None
        )

        obj.santali_month = body.get(
            'sMonth',
            ''
        )

        obj.santali_year = (
            body.get('sYear')
            or None
        )

        obj.note = body.get(
            'note',
            ''
        )

    # ========================================================
    # LUNAR EVENT
    #
    # নতুন:
    # day_from
    # day_to
    # ========================================================

    elif kind == 'event':

        obj = obj or Model()

        try:
            month = int(body['month'])
            day_from = int(body['day_from'])
            day_to = int(body['day_to'])

        except (KeyError, TypeError, ValueError):

            return JsonResponse(
                {
                    'error': (
                        'Month, Lunar Day From '
                        'and Lunar Day To are required'
                    )
                },
                status=400
            )

        if day_from < 1 or day_from > 35:
            return JsonResponse(
                {
                    'error': 'Lunar Day From must be between 1 and 35'
                },
                status=400
            )

        if day_to < 1 or day_to > 35:
            return JsonResponse(
                {
                    'error': 'Lunar Day To must be between 1 and 35'
                },
                status=400
            )

        if day_from > day_to:
            return JsonResponse(
                {
                    'error': (
                        'Lunar Day From cannot be '
                        'greater than Lunar Day To'
                    )
                },
                status=400
            )

        obj.month_order = month

        obj.day_from = day_from

        obj.day_to = day_to

        obj.title = body.get(
            'title',
            ''
        )

        obj.description = body.get(
            'description',
            ''
        )

        # ====================================================
        # IMAGE PRESERVE
        #
        # Update করার সময় নতুন image না দিলে
        # পুরনো image থাকবে।
        # ====================================================

        new_image = str(
            body.get('image') or ''
        ).strip()

        if new_image:
            obj.image = new_image

        obj.label = body.get(
            'label',
            ''
        )

        obj.active = True

    # ========================================================
    # SOLAR EVENT
    # ========================================================

    elif kind == 'solar':

        obj = obj or Model()

        obj.date = body['date']

        obj.title = body.get(
            'title',
            ''
        )

        obj.short_description = body.get(
            'description',
            ''
        )

        obj.details = body.get(
            'details',
            ''
        )

        # নতুন image থাকলে update করবে,
        # না থাকলে পুরনো image থাকবে।

        new_image = str(
            body.get('image') or ''
        ).strip()

        if new_image:
            obj.image = new_image

        obj.active = True

    # ========================================================
    # ADVERTISEMENT
    # ========================================================

    elif kind == 'ad':

        obj = obj or Model()

        obj.slot = body['slot']

        obj.business_name = body.get(
            'business_name',
            ''
        )

        # নতুন image থাকলে update করবে,
        # না থাকলে পুরনো image থাকবে।

        new_image = str(
            body.get('image') or ''
        ).strip()

        if new_image:
            obj.image = new_image

        obj.target_url = body.get(
            'target_url',
            ''
        )

        obj.start_date = (
            body.get('start_date')
            or None
        )

        obj.end_date = (
            body.get('end_date')
            or None
        )

        obj.priority = int(
            body.get('priority', 0)
        )

        obj.active = True

    # ========================================================
    # SITE SETTING
    # ========================================================

    elif kind == 'setting':

        obj, _ = Model.objects.get_or_create(
            key=body['key']
        )

        obj.value = body.get(
            'value',
            ''
        )

    # ========================================================
    # SAVE
    # ========================================================

    try:

        obj.save()

    except Exception as e:

        return JsonResponse(
            {
                'error': str(e)
            },
            status=400
        )

    return JsonResponse(
        {
            'ok': True,
            'id': obj.id
        }
    )


# ============================================================
# ১০. CSV IMPORT
# ============================================================

@login_required
@require_http_methods(['POST'])
def import_csv(request, kind):

    if not request.user.is_staff:
        return JsonResponse(
            {
                'error': 'Admin login required'
            },
            status=403
        )

    if 'file' not in request.FILES:
        return JsonResponse(
            {
                'error': 'CSV file required'
            },
            status=400
        )

    try:

        raw = request.FILES['file'].read().decode(
            'utf-8-sig'
        )

        reader = csv.DictReader(
            io.StringIO(raw)
        )

        count = 0

        for r in reader:

            # =================================================
            # HISTORY
            # =================================================

            if kind == 'history':

                HistoricalDate.objects.update_or_create(
                    gregorian=r['gregorian'],
                    defaults={
                        'bengali_day':
                            r.get('bengali_day') or None,

                        'bengali_month':
                            r.get('bengali_month', ''),

                        'bengali_year':
                            r.get('bengali_year') or None,

                        'santali_day':
                            r.get('santali_day') or None,

                        'santali_month':
                            r.get('santali_month', ''),

                        'santali_year':
                            r.get('santali_year') or None,

                        'note':
                            r.get('note', ''),
                    }
                )

                count += 1

            # =================================================
            # NEW MOON
            # =================================================

            elif kind == 'moon':

                NewMoon.objects.update_or_create(
                    date=r['date'],
                    defaults={
                        'lunar_year':
                            r.get('lunar_year') or None,

                        'month_order':
                            r.get('month_order') or None,

                        'note':
                            r.get('note', ''),
                    }
                )

                count += 1

            # =================================================
            # LUNAR EVENT
            # =================================================

            elif kind == 'event':

                day_from = int(
                    r.get('day_from')
                    or r.get('day')
                )

                day_to = int(
                    r.get('day_to')
                    or day_from
                )

                if day_from > day_to:
                    raise ValueError(
                        'day_from cannot be greater than day_to'
                    )

                LunarEvent.objects.create(
                    month_order=int(
                        r['month']
                    ),

                    day_from=day_from,

                    day_to=day_to,

                    title=r['title'],

                    description=r.get(
                        'description',
                        ''
                    ),

                    image=r.get(
                        'image',
                        ''
                    ),

                    label=r.get(
                        'label',
                        ''
                    ),

                    active=True
                )

                count += 1

            else:

                return JsonResponse(
                    {
                        'error': (
                            'Unsupported import type'
                        )
                    },
                    status=400
                )

    except (KeyError, ValueError) as e:

        return JsonResponse(
            {
                'error': f'CSV error: {e}'
            },
            status=400
        )

    return JsonResponse(
        {
            'ok': True,
            'count': count
        }
    )


# ============================================================
# ১১. CSV EXPORT
# ============================================================

@login_required
@require_GET
def export_csv(request, kind):

    if not request.user.is_staff:
        return JsonResponse(
            {
                'error': 'Admin login required'
            },
            status=403
        )

    fields = []
    rows = []

    # ========================================================
    # HISTORY
    # ========================================================

    if kind == 'history':

        fields = [
            'gregorian',
            'bengali_day',
            'bengali_month',
            'bengali_year',
            'santali_day',
            'santali_month',
            'santali_year',
            'note',
        ]

        rows = [
            [
                x.gregorian,
                x.bengali_day,
                x.bengali_month,
                x.bengali_year,
                x.santali_day,
                x.santali_month,
                x.santali_year,
                x.note,
            ]
            for x in HistoricalDate.objects.all()
        ]

    # ========================================================
    # NEW MOON
    # ========================================================

    elif kind == 'moon':

        fields = [
            'date',
            'lunar_year',
            'month_order',
            'note',
        ]

        rows = [
            [
                x.date,
                x.lunar_year,
                x.month_order,
                x.note,
            ]
            for x in NewMoon.objects.all()
        ]

    # ========================================================
    # LUNAR EVENT
    # ========================================================

    elif kind == 'event':

        fields = [
            'month',
            'day_from',
            'day_to',
            'title',
            'description',
            'image',
            'label',
        ]

        rows = [
            [
                x.month_order,
                x.day_from,
                x.day_to,
                x.title,
                x.description,
                x.image,
                x.label,
            ]
            for x in LunarEvent.objects.all()
        ]

    else:

        return JsonResponse(
            {
                'error': 'Unsupported export type'
            },
            status=400
        )

    response = HttpResponse(
        content_type='text/csv; charset=utf-8'
    )

    response['Content-Disposition'] = (
        f'attachment; filename={kind}.csv'
    )

    writer = csv.writer(response)

    writer.writerow(fields)

    writer.writerows(rows)

    return response