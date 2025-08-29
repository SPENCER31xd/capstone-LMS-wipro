from marshmallow import Schema, fields, validate

class TransactionCreateSchema(Schema):
    book_id = fields.Int(required=True, validate=validate.Range(min=1))
    days_to_return = fields.Int(missing=14, validate=validate.Range(min=1, max=90))

class TransactionReturnSchema(Schema):
    transaction_id = fields.Int(required=True, validate=validate.Range(min=1))

class TransactionResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    book_id = fields.Int()
    user_name = fields.Str()
    book_title = fields.Str()
    issue_date = fields.DateTime(dump_only=True)
    due_date = fields.DateTime(dump_only=True)
    return_date = fields.DateTime(dump_only=True, allow_none=True)
    status = fields.Str()
    days_overdue = fields.Int()
    created_at = fields.DateTime(dump_only=True)

class TransactionSearchSchema(Schema):
    user_id = fields.Int()
    book_id = fields.Int()
    status = fields.Str(validate=validate.OneOf(['issued', 'returned', 'overdue']))
    overdue_only = fields.Bool(missing=False)
