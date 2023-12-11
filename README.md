# Banknote-blog
 A blog dedicated to presenting content in the field of banknotes

### Windows System Configuration

If you are using a Windows system, you may encounter an issue where the `allauth.account.middleware.AccountMiddleware` needs to be added to your Django project's `MIDDLEWARE` setting in the `settings.py` file.

Open your `settings.py` file and ensure that the following line is included in the `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    # other middleware classes...
    'allauth.account.middleware.AccountMiddleware',
    # other middleware classes...
]
```

### Test Account Information

For test purposes, you can use the following account credentials:

- **Login:** `admin`
- **Password:** `admin`

