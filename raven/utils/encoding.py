"""
raven.utils.encoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import six
import warnings


def force_text(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first, saves 30-40% when s is an instance of
    # six.text_type. This function gets called often in that setting.
    if isinstance(s, six.text_type):
        return s
    if strings_only and is_protected_type(s):
        return s
    try:
        if not isinstance(s, six.string_types):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                if six.PY3:
                    if isinstance(s, bytes):
                        s = six.text_type(s, encoding, errors)
                    else:
                        s = six.text_type(s)
                else:
                    s = six.text_type(bytes(s), encoding, errors)
        else:
            # Note: We use .decode() here, instead of six.text_type(s, encoding,
            # errors), so that if s is a SafeBytes, it ends up being a
            # SafeText at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise DjangoUnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = ' '.join([force_text(arg, encoding, strings_only,
                    errors) for arg in s])
    return s


def transform(value):
    from raven.utils.serializer import transform
    warnings.warn('You should switch to raven.utils.serializer.transform', DeprecationWarning)

    return transform(value)


def to_unicode(value):
    try:
        value = six.text_type(force_text(value))
    except (UnicodeEncodeError, UnicodeDecodeError):
        value = '(Error decoding value)'
    except Exception:  # in some cases we get a different exception
        try:
            value = str(repr(type(value)))
        except Exception:
            value = '(Error decoding value)'
    return value


def to_string(value):
    try:
        return six.binary_type(value.decode('utf-8').encode('utf-8'))
    except:
        return to_unicode(value).encode('utf-8')


def shorten(var, list_length=50, string_length=200):
    from raven.utils.serializer import transform

    var = transform(var)
    if isinstance(var, six.string_types) and len(var) > string_length:
        var = var[:string_length] + '...'
    elif isinstance(var, (list, tuple, set, frozenset)) and len(var) > list_length:
        # TODO: we should write a real API for storing some metadata with vars when
        # we get around to doing ref storage
        # TODO: when we finish the above, we should also implement this for dicts
        var = list(var)[:list_length] + ['...', '(%d more elements)' % (len(var) - list_length,)]
    return var
