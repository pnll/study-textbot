from django.conf.urls import include, url
from .views import BotView
urlpatterns = [
				url(r'^b7cd76b8ee605aefea7d19dbcc37fa6809d3d8aa2e6bf1cc22/?$', BotView.as_view())
			]