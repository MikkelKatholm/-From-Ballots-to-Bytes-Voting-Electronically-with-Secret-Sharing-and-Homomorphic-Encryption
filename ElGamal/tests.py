import sys
sys.path.append("../")
import random
import key_gen
from main import *
import unittest
import Shamir.main as shamir



# For all tests we use a 128 bit prime number unless otherwise specified in the test
bits = 128

class TestExample1(unittest.TestCase):

    def test_singleSecretTest(self):
        p, g, pk, sk = gen_keys(bits)
        m = 0 # Message to encrypt
        c = encrypt_for_additive(pk,m,p,g)
        d = decrypt_for_additive(sk,g,c,p,1)

        isSame = d == m
        self.assertTrue(isSame, "Decryption failed")


    def test_additiveTest(self):
        p, g, pk, sk = gen_keys(bits)
        m1 = 0 # Message to encrypt
        m2 = 1 # Message to encrypt
        (c11, c12) = encrypt_for_additive(pk,m1,p,g)
        (c21, c22) = encrypt_for_additive(pk,m2,p,g)
        
        c = (c11*c21, c12*c22)

        d = decrypt_for_additive(sk,g,c,p,2)
        isSame = d == (m1+m2)
        self.assertTrue(isSame, "Decryption failed")

    
    def test_multiplicativeTest(self):
        p, g, pk, sk = gen_keys(bits)
        c1, c2 = 1,1
        totalVote = 0
        voters = 100
        for _ in range(voters):
            m = random.SystemRandom().randint(0,1)
            totalVote += m
            c = encrypt_for_additive(pk,m,p,g)
            c1 *= c[0]
            c2 *= c[1]
        c = (c1,c2)


        result = decrypt_for_additive(sk,g,c,p, voters)

        isSame = result == totalVote
        self.assertTrue(isSame, "Decryption failed")
 

    def test_shamir(self):
        bits = 12
        p, g, pk, sk = gen_keys(bits)
        q = (p-1)//2





        m1 = 0
        keyHolders = 3
        threshold = 2
        shares = generate_key_shares(sk, keyHolders, threshold, q)
        skRec = shamir.reconstruct_secrets(shares, 1,q)
        self.assertEqual([sk], skRec)


        c = encrypt_for_shamir(pk, m1, g, p)
        
        c1, _ = c
        dis = [(share[0], calculate_di_for_shamir(c1, share, p)) for share in shares]   # Correct, tested by hand
        result = decrypt_for_shamir(dis, c, g, threshold, p)

        isSame = result == m1
        self.assertTrue(isSame, "Decryption failed")


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestExample1))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())

    # Format the "ok" messages in a straight line
    print("\n")
    print("Test ran: ", result.testsRun)
    print("Errors: ", len(result.errors))
    print("Failures: ", len(result.failures))
    print("Skipped: ", len(result.skipped))
    print("Success: ", result.wasSuccessful())
    print("\n")

