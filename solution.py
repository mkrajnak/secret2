#!/usr/bin/env python3
import sys


class Curve:
    """Class defining curve and required methods"""
    def __init__(self, fp, a, b, P):
        self.fp = fp    # modulus
        self.a = a      # members of the group
        self.b = b
        try:
            assert self.is_valid()
        except Exception:
            print(f"Invalid curve params\na: {a}\nb: {b}\nfp: {fp}")
            exit(1)

        self.P = P      # Starting point
        self.is_valid_point(self.P)

    def is_valid(self):
        """ Check if a, b are valid (4a^3 + 27b^2) % p != 0"""
        return (4 * (self.a ** 3) + 27 * (self.b ** 2)) % self.fp != 0

    def is_valid_point(self, P):
        """
        Coordinates of point must be lower than fp, (y^2)%fp == (x^3 + ax + b)%fp)
        """
        x, y = P
        assert 0 <= x < self.fp and 0 <= y < self.fp, 'Point outside the group'
        LS = (y ** 2) % self.fp
        PS = (x ** 3 + self.a * x + self.b) % self.fp
        assert LS == PS, 'Point not valid - equation'

    def inv(self, y):
        """ from Fermats theorem """
        return pow(y, self.fp-2, self.fp)

    def add_equal_points(self, P):
        """ s = 3*xp^2 +a / (2 * yp) == s = 3*xp^2 +a * (2 * yp)^-1 """
        xp, yp = P
        s = ((3 * xp ** 2 + self.a) * self.inv(2 * yp)) % self.fp
        xr = (s ** 2 - xp - xp) % self.fp
        yr = (s * (xp - xr) - yp) % self.fp
        return (xr, yr)

    def add_points(self, P, Q):
        """ s = (yq - yp) / (xq - xp) == (yq - yp) (xq - xp)^-1 """
        xp, yp = P
        xq, yq = Q
        s = ((yq - yp) * self.inv(xq - xp)) % self.fp
        xr = (s ** 2 - xp - xq) % self.fp
        yr = (s * (xp - xr) - yp) % self.fp
        return (xr, yr)

    def add_on_ecc(self, P):
        if P == self.P:
            return self.add_equal_points(P)
        else:
            return self.add_points(P, self.P)


def parse_input(input):
    try:
        assert '(' in input
        assert ')' in input
        assert ',' in input
        return tuple(int(x, 0) for x in input.strip('(').strip(')').split(','))
    except Exception:
        print("Usage\n$ make decipher publicKey=\"(0x477...3e, 0xaa0...dc)\"")
        exit(1)


if __name__ == '__main__':
    PUBKEY = parse_input(sys.argv[1])
    curve = Curve(
        fp=0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        a=-0x3,
        b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
        P=(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
           0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
        )
    # test = Curve(fp=23, a=1, b=1, P=(13, 16))
    try:
        curve.is_valid_point(PUBKEY)
    except Exception:
        print("Public Key is not present on the given curve")
        exit(1)

    k = 1
    NP = curve.P
    while NP != PUBKEY:
        NP = curve.add_on_ecc(NP)
        k += 1

    print(k)
