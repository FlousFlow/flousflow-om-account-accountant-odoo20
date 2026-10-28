from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountWorkingFileTemplate(models.Model):
    _name = "account.working.file.template"
    _description = "Accounting Working File Checklist Template"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    section = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class AccountWorkingFile(models.Model):
    _name = "account.working.file"
    _description = "Accounting Working File"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"
    _check_company_auto = True

    _company_name_unique = models.Constraint(
        "UNIQUE(company_id, name)",
        "An accounting working file with this name already exists for this company.",
    )

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company,
        index=True, tracking=True,
    )
    date_from = fields.Date(string="Start Date", required=True, tracking=True)
    date_to = fields.Date(string="End Date", required=True, tracking=True)
    state = fields.Selection(
        [("in_progress", "In Progress"), ("validated", "Validated")],
        default="in_progress", required=True, copy=False, tracking=True, index=True,
    )
    check_ids = fields.One2many(
        "account.working.file.check", "file_id", string="Review Checks", copy=True,
    )
    check_count = fields.Integer(compute="_compute_progress", store=True)
    reviewed_count = fields.Integer(compute="_compute_progress", store=True)
    progress = fields.Float(compute="_compute_progress", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")

    @api.depends("check_ids", "check_ids.state")
    def _compute_progress(self):
        for record in self:
            checks = record.check_ids
            completed = checks.filtered(lambda check: check.state == "reviewed")
            record.check_count = len(checks)
            record.reviewed_count = len(completed)
            record.progress = 100.0 * len(completed) / len(checks) if checks else 0.0

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_to and record.date_to < record.date_from:
                raise ValidationError(_("The end date cannot be earlier than the start date."))

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if "check_ids" in fields_list:
            templates = self.env["account.working.file.template"].search(
                [("active", "=", True)]
            )
            values["check_ids"] = [
                fields.Command.create({
                    "sequence": template.sequence,
                    "section": template.section,
                    "name": template.name,
                    "description": template.description,
                    "template_id": template.id,
                })
                for template in templates
            ]
        return values

    @api.model_create_multi
    def create(self, vals_list):
        files = super().create(vals_list)
        templates = self.env["account.working.file.template"].search([("active", "=", True)])
        for vals, file_record in zip(vals_list, files):
            if "check_ids" not in vals:
                file_record.check_ids = [
                    fields.Command.create({
                        "sequence": template.sequence,
                        "section": template.section,
                        "name": template.name,
                        "description": template.description,
                        "template_id": template.id,
                    })
                    for template in templates
                ]
            file_record.message_post(body=_("Working file created for %(name)s.", name=file_record.name))
        return files

    def action_validate(self):
        if not self.env.user.has_group("account.group_account_manager"):
            raise AccessError(_("Only accounting managers can validate a working file."))
        for file_record in self:
            if file_record.state == "validated":
                continue
            if not file_record.check_ids:
                raise UserError(_("Load or add review checks before validating this working file."))
            pending = file_record.check_ids.filtered(
                lambda check: check.state != "reviewed"
            )
            if pending:
                raise UserError(_("Every review check must be reviewed before validation."))
            super(AccountWorkingFile, file_record).write({"state": "validated"})
            file_record.message_post(body=_("Working file validated."))
        return True

    def action_reopen(self):
        if not self.env.user.has_group("account.group_account_manager"):
            raise AccessError(_("Only accounting managers can reopen a working file."))
        for file_record in self:
            super(AccountWorkingFile, file_record).write({"state": "in_progress"})
        self.message_post(body=_("Working file reopened for changes."))
        return True

    def write(self, vals):
        if "state" in vals:
            raise UserError(_("Use the Validate or Reopen action to change the working file status."))
        if any(file_record.state == "validated" for file_record in self):
            raise UserError(_("Reopen the working file before changing it."))
        return super().write(vals)

    def unlink(self):
        if any(file_record.state == "validated" for file_record in self):
            raise UserError(_("Reopen the working file before deleting it."))
        return super().unlink()


class AccountWorkingFileCheck(models.Model):
    _name = "account.working.file.check"
    _description = "Accounting Working File Review Check"
    _inherit = ["mail.thread"]
    _order = "sequence, id"
    _check_company_auto = True

    file_id = fields.Many2one(
        "account.working.file", required=True, ondelete="cascade", index=True,
        check_company=True,
    )
    company_id = fields.Many2one(related="file_id.company_id", store=True, index=True)
    template_id = fields.Many2one(
        "account.working.file.template", ondelete="set null", copy=False,
    )
    sequence = fields.Integer(default=10)
    section = fields.Char(required=True, translate=True)
    name = fields.Char(required=True, translate=True)
    description = fields.Text(translate=True)
    state = fields.Selection(
        [("pending", "Pending Review"), ("reviewed", "Reviewed")],
        default="pending", required=True, tracking=True, index=True,
    )
    reviewer_id = fields.Many2one("res.users", readonly=True, copy=False, tracking=True)
    reviewed_on = fields.Datetime(readonly=True, copy=False, tracking=True)
    note = fields.Text(tracking=True)
    evidence = fields.Binary(attachment=True)
    evidence_filename = fields.Char()

    def write(self, vals):
        if any(check.file_id.state == "validated" for check in self):
            raise UserError(_("Reopen the working file before changing its review checks."))
        if vals.get("state") == "reviewed":
            vals = {**vals, "reviewer_id": self.env.user.id, "reviewed_on": fields.Datetime.now()}
        elif vals.get("state") == "pending":
            vals = {**vals, "reviewer_id": False, "reviewed_on": False}
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("state") == "reviewed":
                vals.update(reviewer_id=self.env.user.id, reviewed_on=fields.Datetime.now())
        return super().create(vals_list)

    def unlink(self):
        if any(check.file_id.state == "validated" for check in self):
            raise UserError(_("Reopen the working file before removing its review checks."))
        return super().unlink()
