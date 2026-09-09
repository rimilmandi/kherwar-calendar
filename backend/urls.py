from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from store import views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', admin.site.urls),  # উভয় admin URL রাখতে পারেন
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', TemplateView.as_view(template_name='index.html'), name='calendar'),
    path('admin-panel/', views.admin_panel, name='admin-panel'),
    path('api/calendar/bootstrap/', views.bootstrap, name='bootstrap'),
    path('api/calendar/month/', views.calendar_month, name='calendar_month'),
    path('api/calendar/data/<str:kind>/', views.data_api, name='data_api'),
    path('api/calendar/import/<str:kind>/', views.import_csv, name='import_csv'),
    path('api/calendar/export/<str:kind>/', views.export_csv, name='export_csv'),
    path('api/calendar/upload-image/', views.upload_image, name='upload_image'),
]

# ডেভেলপমেন্টে static ও media ফাইল সার্ভ করা
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)