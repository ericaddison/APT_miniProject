import os

from google.appengine.api import users

from google.appengine.api import app_identity
from source.models.NdbClasses import *
import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler
from google.appengine.ext.webapp import template
import json


class GeoMapPage(BaseHandler):
    def get(self):
        user = StreamUser.get_current_user(self)

        if user:
            nickname = user.nickName
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return

        all_streams = Stream.get_all_streams()
        item_data = []
        for stream in all_streams:
            items = stream.get_all_items()
            for i in range(len(items)):
                item = items[i]
                prev_ind = i - (i % 10) + 1
                stream_url = fh.get_viewstream_url(stream.get_id(), prev_ind, prev_ind+9, i-prev_ind+1)
                if item.getLatLng() is not None:
                    item_data.append({
                                        "lat": item.latitude,
                                        "lng": item.longitude,
                                        "url": item.URL,
                                        "stream_name": stream.name,
                                        "stream_url": stream_url,
                                        "date_added": str(item.dateAdded)
                                    })
        
        template_values = {
            'html_template': 'MasterTemplate.html',
            'user': nickname,
            'login_url': login_url,
            'login_text': login_text,
            'item_data': item_data
        }

        path = os.path.join(os.path.dirname(__file__), '../../templates/GeoMap.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))

