from marshmallow import Schema, fields, validate, post_load
from models.user import UserRole, UserStatus

class UserRegistrationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=100))
    role = fields.Str(missing='member', validate=validate.OneOf(['admin', 'member']))

class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Str()
    role = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=100))
    status = fields.Str(validate=validate.OneOf(['active', 'blocked']))

class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6, max=100))
