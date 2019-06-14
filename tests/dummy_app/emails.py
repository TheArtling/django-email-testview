from email_testview.registry import registry


def fixtures():
    return ['Test message'], {}


def dummy_email(message):
    return {
        'context': {
            'message': message,
        },
    }


registry.register('dummy_app.dummy_email', dummy_email, fixtures)
