import os

import source.Framework.Framework_Helpers as fh
from source.Framework.BaseHandler import BaseHandler


class ErrorView(BaseHandler):
    def get(self):

        error_code = self.get_request_param(fh.error_code_parm)
        error_string = self.get_request_param(fh.message_parm)

        # no error error_code in URL
        if error_code in [None, '']:
            error_code = -1

        if error_string in [None, '']:
            error_string = "An error has occurred!"

        else:
            # get error error_code from URL and convert unicode to integer
            error_code = int(error_code)

            # if error error_code in dictionary, look it up.
            if error_code in fh.error_codes:
                error_string = fh.error_codes[error_code]

        template_values = {
            'error_code': error_code,
            'error_string': error_string
        }

        path = os.path.join(os.path.dirname(__file__), '../../templates/ErrorView.html')
        self.set_content_text_html()
        self.write_response(fh.render_html_template(path, template_values))
