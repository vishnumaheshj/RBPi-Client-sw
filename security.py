#
# import the CryptContext class, used to handle all hashing...
#
from passlib.context import CryptContext

#
# create a single global instance for your app...
#
hashInterface = CryptContext(
    # Replace this list with the hash(es) you wish to support.
    schemes=["argon2",],

    # Automatically mark all but first hasher in list as deprecated.
    # (this will be the default in Passlib 2.0)
    deprecated="auto",

    # Optionally, set the number of rounds that should be used.
    # Appropriate values may vary for different schemes,
    # and the amount of time you wish it to take.
    # Leaving this alone is usually safe, and will use passlib's defaults.
    )
