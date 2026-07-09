# otp.py

OTP_STATIQUE = "123456"  # simule pour la phase 1 ( a changer )

class OTP:
    def __init__(self, code: str):
        self.code = code

    def is_valid(self) -> bool:
        return self.code == OTP_STATIQUE
