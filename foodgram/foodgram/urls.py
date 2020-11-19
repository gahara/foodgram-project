from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from .views import page_not_found, server_error

handler404 = page_not_found
handler500 = server_error

urlpatterns = [
    path('admin/', admin.site.urls),
    # это нужно чтобы все урлы, относящиеся к профилю начинались одинаково с
    # auth
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    path('about-us/', views.flatpage, {
        'url': '/about-us/'}, name='about-author'),
    path('about-spec/', views.flatpage, {
        'url': '/about-spec/'}, name='about-spec'),
    path('', include('products.urls'))
]
