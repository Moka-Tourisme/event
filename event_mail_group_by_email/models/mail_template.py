# Copyright 2021 Camptocamp SA - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, models
from odoo.exceptions import UserError


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _get_extra_records_attachments(self, res_ids):
        self.ensure_one()
        attachments = []
        for res_id in res_ids:
            template = self
            report_name = template._render_field(
                'report_name', [res_id], compute_lang=True)[res_id]
            report = template.report_template
            report_service = report.report_name

            if report.report_type in ['qweb-html', 'qweb-pdf']:
                result, format_report = report._render_qweb_pdf([res_id])
            else:
                res = report._render([res_id])
                if not res:
                    raise UserError(_('Unsupported report type %s found.', report.report_type))
                result, format_report = res

            result = base64.b64encode(result)
            if not report_name:
                report_name = 'report.' + report_service
            ext = "." + format_report
            if not report_name.endswith(ext):
                report_name += ext
            attachments.append((report_name, result))
        return attachments

    def generate_email(self, res_ids, fields=None):
        # If records is available in context, and the template has a report,
        # render and attach reports for all extra record.
        # Note: multi_mode is out of scope.
        self.ensure_one()
        res = super().generate_email(res_ids, fields=fields)
        records = self.env.context.get("records")
        if (
            self.env.context.get("group_by_email")
            and records
            and self.report_template
            and isinstance(res_ids, int)
        ):
            extra_res_ids = list(set(records.ids) - {res_ids})
            extra_attachments = self._get_extra_records_attachments(extra_res_ids)
            res.setdefault("attachments", [])
            res["attachments"] += extra_attachments
        return res
