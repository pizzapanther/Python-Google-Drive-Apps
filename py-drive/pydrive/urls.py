from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^$', 'editor.views.home', name='home'),
  url(r'^shatner$', 'editor.views.shatner', name='shatner'),
)
