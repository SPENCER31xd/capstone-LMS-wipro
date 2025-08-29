from marshmallow import Schema, fields, validate

class BookCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    author = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    total_copies = fields.Int(required=True, validate=validate.Range(min=1))

class BookUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    author = fields.Str(validate=validate.Length(min=1, max=100))
    category = fields.Str(validate=validate.Length(min=1, max=50))
    total_copies = fields.Int(validate=validate.Range(min=1))

class BookResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    author = fields.Str()
    category = fields.Str()
    total_copies = fields.Int()
    available_copies = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class BookSearchSchema(Schema):
    title = fields.Str()
    author = fields.Str()
    category = fields.Str()
    available_only = fields.Bool(missing=False)
