import json
import os

import urllib2

from datetime import datetime

from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from google.appengine.api import users

import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler

DEFAULT_IMAGES_PER_PAGE = 10
images_per_page = DEFAULT_IMAGES_PER_PAGE


class ViewStream(BaseHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            nickname = user.nickname()
            login_url = users.create_logout_url('/')
            login_text = 'Sign out'
        else:
            self.redirect("/")
            return


        # retrieve request parameters
        stream_id = self.get_request_param(fh.stream_id_parm)

        # retrieve the stream from the ID
        try:
            stream = (ndb.Key('Stream', int(stream_id))).get()
        except:
            self.redirect('/')
            return

        if stream is None:
            self.redirect('/')
            return

        active_image = self.get_request_param(fh.active_image_parm)
        try:
            active_image = int(active_image)
        except (TypeError, ValueError):
            active_image = 0

        #Increment view counter
        stream.viewList.append(datetime.now())
        stream.numViews = stream.numViews+1
        stream.put()
        
        upload_url = blobstore.create_upload_url('/services/upload')

        # get the current image range
        ind1, ind2, status = fh.get_image_range_param(self)
        if ind1 is None or ind2 is None:
            ind1 = 1
            ind2 = images_per_page

        # make call to viewimage service
        viewstream_service_url = fh.get_viewstream_service_url(stream_id, ind1, ind2)

        result = urllib2.urlopen(viewstream_service_url)
        response = json.loads("".join(result.readlines()))
        image_urls = response['urls']
        tags = response[fh.tags_parm]
        tags = [{'name': tag, 'url': fh.get_viewtag_url(tag)} for tag in tags]
        
        #Values for GeoMap
        streamItemsLoc = response['streamItemsLoc']

        # get total number of images and make links
        num_images = response[fh.num_images_parm]

        # get next 10 images link
        next_page_url = None
        if ind2 < num_images:
            next_page_url = fh.get_viewstream_url(stream_id, ind1+images_per_page, ind2+images_per_page)

        # get previous 10 images link
        prev_page_url = None
        if ind1 > 1:
            prev_page_url = fh.get_viewstream_url(stream_id, ind1-images_per_page, ind2-images_per_page)

        # see if user is subscribed to this stream
        # make call to subscribed service
        subscribed_service_url = fh.get_subscribed_service_url(user.user_id(), stream_id)

        result = urllib2.urlopen(subscribed_service_url)
        response = json.loads("".join(result.readlines()))
        is_subscribed = response['status']

        redirect_url = urllib2.quote(fh.get_viewstream_url(stream_id, ind1, ind2))
        if is_subscribed:
            sub_url = fh.get_unsubscribe_service_url(user.user_id(), stream_id, redirect_url)
        else:
            sub_url = fh.get_subscribe_service_url(user.user_id(), stream_id, redirect_url)

        template_values = {
                    'html_template': 'MasterTemplate.html',
                    'stream': stream,
                    'stream_id': stream.stream_id(),
                    'upload_url': upload_url,
                    'image_urls': image_urls,
                    'user': user,
                    'login_url': login_url,
                    'login_text': login_text,
                    'is_subscribed': is_subscribed,
                    'sub_url': sub_url,
                    'tags': tags,
                    'tag_name_parm': fh.tag_name_parm,
                    'tag_url': fh.get_tagmod_url_noparm(),
                    'redirect_url': self.get_current_url(),
                    'stream_id_parm': fh.stream_id_parm,
                    'redirect_parm': fh.redirect_parm,
                    'url_parm': fh.url_parm,
                    'streamItemsLoc': json.dumps(streamItemsLoc),
                    'active_image': active_image
                }

        if next_page_url:
            template_values['next_page_url'] = next_page_url

        if prev_page_url:
            template_values['prev_page_url'] = prev_page_url

        path = os.path.join(os.path.dirname(__file__), '../../templates/ViewStream.html')
        self.response.write(template.render(path, template_values))


class TagMod(BaseHandler):
    def post(self):

        button = self.get_request_param('submit')
        stream_id = self.get_request_param(fh.stream_id_parm)
        tag_name = self.get_request_param(fh.tag_name_parm)

        if button == 'Add Tag':
            tag_service_url = fh.get_addtag_service_url(stream_id, tag_name)
        elif button == 'Remove Tag':
            tag_service_url = fh.get_removetag_service_url(stream_id, tag_name)

        urllib2.urlopen(tag_service_url)

        redirect_url = str(self.get_request_param(fh.redirect_parm))

        if redirect_url in ['', None]:
            self.redirect('/')
        else:
            self.redirect(redirect_url)


