import json
from source.Framework.BaseHandler import BaseHandler
import source.Framework.RebuildSearchIndices as rb

# Cron jobs for Rebuilding Search Indices
# to run every hour
#


class CronRebuildSearchIndexService(BaseHandler):

    def get(self):
        rb.rebuild_tag_index()
        rb.rebuild_stream_index()
        self.write_response(json.dumps("{'reponse': 'Done rebuilding indices'}"))
