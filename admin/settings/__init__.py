import os

# Get the ENV setting. Needs to be set in .bashrc or similar.
ENV = os.environ.get('ENV')
if not ENV:
    raise Exception('Environment variable ENV is required!')

overrides = __import__(
    ENV,
    globals(),
    locals(),
    ['admin', 'settings'],
    1,
)

# apply imported overrides
for attr in dir(overrides):
    # we only want to import settings (which have to be variables in ALLCAPS)
    if attr.isupper():
        globals()[attr] = getattr(overrides, attr)
