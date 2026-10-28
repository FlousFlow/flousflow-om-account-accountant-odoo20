from odoo import api, fields, models


ACCOUNTING_READ_GROUPS = ",".join([
    "account.group_account_readonly",
    "account.group_account_invoice",
    "account.group_account_user",
    "account.group_account_manager",
])


class SaleOrderLineReviewCost(models.Model):
    _inherit = "sale.order.line"

    review_accrual_unit_cost = fields.Monetary(
        string="Unit Cost",
        currency_field="currency_id",
        compute="_compute_review_accrual_unit_cost",
        store=True,
        readonly=False,
        groups=ACCOUNTING_READ_GROUPS,
    )
    review_accrual_delivered_total_cost = fields.Monetary(
        string="Delivered Total Cost",
        currency_field="currency_id",
        compute="_compute_review_accrual_delivered_total_cost",
        store=True,
        groups=ACCOUNTING_READ_GROUPS,
    )
    review_accrual_invoiced_total_cost = fields.Monetary(
        string="Invoiced Total Cost",
        currency_field="currency_id",
        compute="_compute_review_accrual_invoiced_total_cost",
        store=True,
        groups=ACCOUNTING_READ_GROUPS,
    )

    @api.depends("product_id", "company_id", "currency_id", "product_uom_id")
    def _compute_review_accrual_unit_cost(self):
        for line in self:
            product = line.product_id
            if not product or not line.product_uom_id:
                line.review_accrual_unit_cost = 0.0
                continue
            company_line = line.with_company(line.company_id)
            product_cost = product.uom_id._compute_price(
                product.standard_price, line.product_uom_id
            )
            line.review_accrual_unit_cost = company_line._convert_to_sol_currency(
                product_cost, product.cost_currency_id
            )

    @api.depends("review_accrual_unit_cost", "qty_delivered")
    def _compute_review_accrual_delivered_total_cost(self):
        for line in self:
            line.review_accrual_delivered_total_cost = (
                line.review_accrual_unit_cost * line.qty_delivered
            )

    @api.depends("review_accrual_unit_cost", "qty_invoiced")
    def _compute_review_accrual_invoiced_total_cost(self):
        for line in self:
            line.review_accrual_invoiced_total_cost = (
                line.review_accrual_unit_cost * line.qty_invoiced
            )
