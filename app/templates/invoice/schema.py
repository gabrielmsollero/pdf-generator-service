from marshmallow import fields, Schema


class InvoiceItemSchema(Schema):
    description = fields.String(required=True)
    unit_price = fields.Float(required=True)
    quantity = fields.Integer(required=True)


class InvoiceSchema(Schema):
    invoice_number = fields.String(required=True)
    account_number = fields.String(required=True)
    emission_date = fields.Date(required=True, format="%Y/%m/%d")
    due_by = fields.Date(required=True, format="%Y/%m/%d")
    total_due = fields.Float(required=True)
    items = fields.List(fields.Nested(InvoiceItemSchema), required=True)


schema = InvoiceSchema()
