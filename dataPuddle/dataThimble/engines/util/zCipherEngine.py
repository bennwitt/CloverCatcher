import hashlib
import hmac

secretKey16bytes = "1234567890123456"
secretKey = "xyz"
secretKey16bytes = secretKey16bytes.encode("utf-8")


def verifyAuthToken(string, token):
    emailAddress = emailAddress.strip().lower()
    userAuthToken = userAuthToken.strip().lower()

    verificationToken = generateAuthToken(emailAddress)
    verificationStatus = hmac.compare_digest(verificationToken, userAuthToken)
    return verificationStatus


def generateAuthToken(emailAddress):
    emailAddress = emailAddress.strip().lower()

    generatedAuthToken = hmac.new(
        secretKey.encode(), emailAddress.encode(), hashlib.sha256
    ).hexdigest()[
        :6
    ]  # First 6 characters
    return generatedAuthToken
