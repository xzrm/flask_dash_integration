
from project import admin
from .models import *
from flask_admin.contrib.sqla import ModelView
from flask import redirect, abort, url_for
from flask_login import current_user


class MyModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('login'))


    # can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True


admin.add_view(MyModelView(Project, db.session))
admin.add_view(MyModelView(User, db.session))