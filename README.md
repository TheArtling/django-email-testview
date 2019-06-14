# Django Email Testview

This is a highly opinionated little helper tool that helps us at The Artling to
test our email templates. It is quite possible that you will not be able to use
this in your project because it would require you to refactor tons of your code,
which might not be worth the effort.

However, you could always add this app to your project and then just use it for
new email templates and you can gradually migrate old emails to this new
framework over time.

## The problem

Our app sends tons of different email notifications to our users and our admins.
In the worst situation, a developer would click around in the frontend until
they reach the point where a certain email would be triggered. Then keep
refreshing GMail until the email arrives, look at it, then make a few changes,
then trigger it again. This is an incredibly frustrating and time consuming
workflow.

## The solution

We would like to have one view `/emails/test/` which can only be accessed by
admins and which shows a list of all emails that are registered in the system.
When you click at one of those links, it should show a view that simply renders
that email template in the browser.

The only tricky part with this is that most emails need quite complicated
template contexts in order to render all the stuff that should be shown in the
email. It would be nice if this "email testview" would not just render the
template with fixture values, but even call the real function that prepares the
email context, so that this view would crash in the case when there are bugs in
that function.

## The opinionated approach

With this app, you will create your emails as follows:

### Step 1: Create your email template

Let's say you have an app called `contact`. First, you will create the email
templates in that app:

```
contact
-- templates
----- contact
-------- email
----------- body
-------------- new_contact_request.html
----------- subject
-------------- new_contact_request.html
```

By convention, the files for the email `body` and the email `subject` must have
an identical name and they must be located in an
`appname/templates/appname/email/` folder .

### Step 2: Create your email function

Just like many Django apps have a `models.py` or an `admin.py`, you will now
add an `emails.py` to your app. It will look something like this:

```py
from email_testview.registry import registry


def new_contact_email_fixtures():
    return ['Test message'], {'first_name': 'First', 'last_name': 'Last'}


def new_contact_email(message, first_name=None, last_name=None):
    return {
        'context': {
            'message': message,
            'first_name': first_name,
            'last_name': last_name,
        },
        # These are optional:
        # 'from_email': 'someone@example.com',  # default: settings.FROM_EMAIL
        # 'recipients': ['someone@example.com'],  # default: the first from settings.ADMINS
    }


registry.register('contact.new_contact_email', new_contact_email, new_contact_email_fixtures)
```

You can see that writing an email consists of three parts:

1. First you write your actual email function (here: `new_contact_email()`).
   Your email function will probably take in some arguments, usually some
   instance from your database or other values that should be rendered in the
   email. This function simply returns the context that shall be passed into the
   email template.
2. Next you write a fixtures function that will return exactly the `*args` and
   `**kwargs` that your email function needs. We use tools like `mixer` here
   (with `commit=False`) in order to create complex object structures (like a
   user's cart with cart items and all that) with just a few lines of code.
3. Finally you register this email to a central registry, similar how you would
   also register your Django admin classes.

**Why do we like this?**

The nice thing about all this is that whenever someone needs to design a new
email, they will probably look into an already existing `emails.py` and quickly
understand this three-step-pattern, then copy and paste one old email and just
change around all the values as needed. Also, whenever you need to change the
context for an old email, you will have the corresponding fixtures function
right above it and you will remember that you might have to change the fixtures
as well.

Another cool thing is, that in both cases, when the server actually sends an
email and when the developer looks at the email in the `/emails/test/` view, the
exact same email function will be called, so if there are bugs in that email
function, it is more likely that the developer is going to see them while
designing the email.

### Step 3: Send your email

This app comes with a `send_mail` function that you can use like this:

```py
from email_testview.utils import send_mail

message = 'Some message'
first_name = 'First'
last_name = 'Last'
send_mail('contact.new_contact_email', message, first_name=first_name, last_name=last_name)
```

The `send_mail` function will pass the given `*args` and `**kwargs` into your
email function `new_contact_email()`. It will then look at the email identifier
that you have given (`contact.new_contact_email`) and figure out the template
name.

This means: Your email function name and the template name must be identical!

### Step 4: Profit

You can now login as an admin, go to `/emails/test/` click at the email that you
want to modify, see the email in your browser and start modifying the html and
the css and see the results in your browser immediately.

# Installation

Install via pip:

```
pip install django-email-testview
```

Add to your `INSTALLED_APPS` settings:

```py
INSTALLED_APPS = [
    # ...
    'email_testview',
]
```

Add to your main `urls.py`:

```py
urlpatterns = [
    re_path(r'admin/', admin.site.urls),
    # ...
    re_path(r'emails/', include('email_testview.urls')),
]
```

Add to your `local_settings.py`:

```py
ENVIRONMENT = 'local'
```

This is just another safeguard to make sure that this view can never be accessed
on a production environment. Our production environments have this setting set
to `prod` and when that is the case, then the view will return a 403 error..

Create an `emails.py` file in one of your apps, as described above. Make sure
that you are logged in as an admin user and visit `/emails/test/`.
