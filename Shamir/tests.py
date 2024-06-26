from main import *
import sympy.ntheory as nt
import random
import unittest


class TestExample1(unittest.TestCase):

    """ 
    Expected result is generated by https://www.extendedeuclideanalgorithm.com/calculator.php
    """
    def test_extended_euclid_gcd(self):
        inputs = [(10,5), (15, 8), (41, 13), (100, 10), (100, 3), (100, 1), (1203, 123)]
        expected = [(5,0,1), (1,-1,2),(1,-6,19),(10,0,1),(1,1,-33),(1,0,1),(3,9,-88)]
        for i in range(len(inputs)):
            a, b = inputs[i]
            d, x, y = extended_euclid_gcd(a, b)
            self.assertEqual((d, x, y), expected[i])



    def test_all(self):
        secret = [1234]
        numOfShares = 6
        threshold = 3
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold,fieldsize)

        reconstructedSecret1 = reconstruct_secrets(shares[:threshold], 1, fieldsize)
        reconstructedSecret2 = reconstruct_secrets(shares[-threshold:], 1, fieldsize)
        isSame = secret == reconstructedSecret1 == reconstructedSecret2
        self.assertTrue(isSame)

    def test_more_shares_than_needed(self):
        secret = [1234]
        numOfShares = 10
        threshold = 3
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold,fieldsize)

        reconstructedUsingThreshold = reconstruct_secrets(shares[:threshold], 1, fieldsize)
        reconstructedSecretALlSHares = reconstruct_secrets(shares, 1, fieldsize)
        isSame = secret == reconstructedUsingThreshold == reconstructedSecretALlSHares
        self.assertTrue(isSame)

    def test_with_different_primes(self):
        # Generate a list of primes
        startingPrime = 1619
        primes = [startingPrime]
        nums = [2**i for i in range(12,100)]
        for i in range(len(nums)):
            workingPrime = nt.nextprime(nums[i] )
            primes.append(workingPrime)

        for i in range(len(primes)):
            workingPrime = primes[i]
            secret = [1234]
            numOfShares = 6
            threshold = 3

            shares = split_secrets(secret, numOfShares, threshold, workingPrime)

            reconstructedSecret1 = reconstruct_secrets(shares[:threshold], 1, workingPrime)
            reconstructedSecret2 = reconstruct_secrets(shares[-threshold:], 1, workingPrime)

            isSame = secret == reconstructedSecret1 == reconstructedSecret2
            self.assertTrue(isSame)


    def test_one_lies(self):
        secret = [1234]
        numOfShares = 6
        threshold = 3
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold,fieldsize)

        # One share lies 
        shares[0] = (shares[0][0], shares[0][1] - 1)

        reconstructedSecret1 = reconstruct_secrets(shares[:threshold], 1, fieldsize)
        reconstructedSecret2 = reconstruct_secrets(shares[-threshold:], 1, fieldsize)
        self.assertNotEqual(secret, reconstructedSecret1)
        self.assertEqual(secret, reconstructedSecret2)

    def test_detect_errors(self):
        secret = [1234]
        numOfShares = 6
        threshold = 3
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold,fieldsize)

        # One share lies 
        shares[5] = (shares[5][0], shares[5][1] - 1)

        foundErrors = detect_error(shares, threshold, fieldsize)

        self.assertTrue(foundErrors)

    def test_additive_test(self):
        secret1 = [1]
        secret2 = [1]
        secret3 = [0]
        threshold = 2
        numOfShares = 3
        fieldsize = 1613

        #Contruct the shares for each secret
        shares1 = split_secrets(secret1, numOfShares, threshold, fieldsize)
        shares2 = split_secrets(secret2, numOfShares, threshold, fieldsize)
        shares3 = split_secrets(secret3, numOfShares, threshold, fieldsize)

        #Add the shares together
        shares = []
        for i in range(3):
            shares.append((shares1[i][0], (shares1[i][1] + shares2[i][1] + shares3[i][1]) % fieldsize))

        #Reconstruct the secret
        reconstructedSecret = reconstruct_secrets(shares, 1, fieldsize)
        assert reconstructedSecret == [2]

        #Recontruct the secret with only 2 shares from each secret
        reconstructedSecret = reconstruct_secrets(shares[:2], 1, fieldsize)
        self.assertEqual(reconstructedSecret, [2])
        

    """
    To reconstruct we must use (numOfSecrets + threshold-1) shares
    """
    def test_multiple_secrets(self):
        secrets = [2,3,4,6,7]
        threshold = 4
        numOfShares = 16
        fieldsize = 1613
        sharedNeeded = len(secrets) + threshold - 1

        shares = split_secrets(secrets, numOfShares, threshold, fieldsize)
        #Reconstruct the secrets
        reconstructedSecret = reconstruct_secrets(shares[:sharedNeeded], len(secrets), fieldsize)
        self.assertEqual(reconstructedSecret, secrets)

    def test_berlekamp_welsh_k_lies(self):
        secret = [1234,10, 20]
        numOfSecrets = len(secret)
        k = 2
        threshold = 5
        finalDegree = threshold + numOfSecrets - 1
        sharedNeeded = threshold + numOfSecrets  - 1
        numOfShares = threshold + 2*k + numOfSecrets - 1 
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold, fieldsize)

        # the last two shares are lying
        shares = shares[:-2] + [(shares[-2][0], shares[-2][1] - 1), (shares[-1][0], shares[-1][1] - 1)]
        # Select 2k+threshold shares at random
        random.shuffle(shares)
    
        # Remove corrupted share
        shares = berlekamp_welsh(shares, k, finalDegree, fieldsize)

        reconstructedSecrets = reconstruct_secrets(shares[:sharedNeeded], numOfSecrets, fieldsize)
        reconstructedSecrets1 = reconstruct_secrets(shares[-sharedNeeded:], numOfSecrets, fieldsize)
        isSame = secret == reconstructedSecrets == reconstructedSecrets1
        self.assertTrue(isSame)

    def test_berlekamp_welsh_k_min_1_Lies(self):
        secret = [1234]
        numOfSecrets = len(secret)
        k = 2
        threshold = 2
        finalDegree = threshold + numOfSecrets - 1
        sharedNeeded = threshold + numOfSecrets  - 1
        numOfShares = threshold + 2*k + numOfSecrets - 1 + 10
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold, fieldsize)
        shares = shares[:-1]+[(shares[-1][0], shares[-1][1] - 1)]

        # Remove corrupted share
        shares = berlekamp_welsh(shares, k, finalDegree, fieldsize)


        reconstructedSecrets = reconstruct_secrets(shares[:sharedNeeded], numOfSecrets, fieldsize)
        reconstructedSecrets1 = reconstruct_secrets(shares[-sharedNeeded:], numOfSecrets, fieldsize)
        isSame = reconstructedSecrets == secret == reconstructedSecrets1 
        self.assertTrue(isSame)
        

    def test_berlekamp_welsh_no_Lies(self):
        secret = [1234]
        numOfSecrets = len(secret)
        k = 2
        threshold = 2
        finalDegree = threshold + numOfSecrets - 1
        sharedNeeded = threshold + numOfSecrets  - 1
        numOfShares = threshold + 2*k + numOfSecrets - 1
        fieldsize = 1613

        shares = split_secrets(secret, numOfShares, threshold, fieldsize)

        # Remove corrupted share
        shares = berlekamp_welsh(shares, k, finalDegree, fieldsize)

        reconstructedSecrets = reconstruct_secrets(shares[:sharedNeeded], numOfSecrets, fieldsize)
        reconstructedSecrets1 = reconstruct_secrets(shares[-sharedNeeded:], numOfSecrets, fieldsize)
        isSame = reconstructedSecrets == secret == reconstructedSecrets1
        self.assertTrue(isSame)

    @unittest.skip("This test is too slow")
    def test_berlekamp_welsh_Loop(self):
        # When the threshold is large the runtime is really long
        # Reduced row echelon form is O(n^3)
        for _ in range(100):
            fieldsize = 1613
            secret = [random.randint(1, fieldsize-1) for i in range(3)]
            numOfSecrets = len(secret)
            threshold = random.randint(3, 5)
            k = random.randint(1, threshold-1)
            finalDegree = threshold + numOfSecrets - 1
            sharedNeeded = threshold + numOfSecrets  - 1
            numOfShares = threshold + 2*k + numOfSecrets - 1 

            shares = split_secrets(secret, numOfShares, threshold, fieldsize)

            # the last k shares are lying
            for i in range(k):
                shares[-1-i] = (shares[-1-i][0], shares[-1-i][1] - 1)


            # Select 2k+threshold shares at random
            random.shuffle(shares)
        
            # Remove corrupted share
            shares = berlekamp_welsh(shares, k, finalDegree, fieldsize)

            reconstructedSecrets = reconstruct_secrets(shares[:sharedNeeded], numOfSecrets, fieldsize)
            reconstructedSecrets1 = reconstruct_secrets(shares[-sharedNeeded:], numOfSecrets, fieldsize)
            isSame = secret == reconstructedSecrets == reconstructedSecrets1
            self.assertTrue(isSame)

    @unittest.skip("This test is too slow")
    def test_additive_berlekamp_welsh(self):
        secret1 = [1,1,5,4,1]
        secret2 = [1,0,4,1,4]
        secret3 = [0,5,4,3,1]
        numOfSecrets = len(secret1)
        finalVotes = [2,6,13,8,6]
        threshold = 5
        k = 5
        sharesNeeded = threshold + numOfSecrets  - 1
        finalDegree = threshold + numOfSecrets - 1
        numOfShares = threshold + 2*k + numOfSecrets - 1 
        fieldsize = 1613

        #Contruct the shares for each secret
        shares1 = split_secrets(secret1, numOfShares, threshold, fieldsize)
        shares2 = split_secrets(secret2, numOfShares, threshold, fieldsize)
        shares3 = split_secrets(secret3, numOfShares, threshold, fieldsize)

        # Make the last k shares lie
        for i in range(k):
            shares1[-1-i] = (shares1[-1-i][0], shares1[-1-i][1] - 1)
            shares2[-1-i] = (shares2[-1-i][0], shares2[-1-i][1] - 1)
            shares3[-1-i] = (shares3[-1-i][0], shares3[-1-i][1] - 1)

        #Add the shares together
        shares = []
        for i in range(numOfShares):
            shares.append((shares1[i][0], (shares1[i][1] + shares2[i][1] + shares3[i][1]) % fieldsize))

        # Shuffle the shares
        random.shuffle(shares)

        # Remove corrupted share
        shares = berlekamp_welsh(shares, k, finalDegree, fieldsize)

        #Reconstruct the secret
        reconstructedSecret1 = reconstruct_secrets(shares, numOfSecrets, fieldsize)

        #Recontruct the secret with only 2 shares from each secret
        reconstructedSecret2 = reconstruct_secrets(shares[:sharesNeeded], numOfSecrets, fieldsize)
        isSame = reconstructedSecret1 == finalVotes == reconstructedSecret2
        self.assertTrue(isSame)

    def test_reconstruction_with_shuffled_shares(self):
        for _ in range(100):
            secret = [1234]
            numOfShares = 6
            threshold = 3
            fieldsize = 1613

            shares = split_secrets(secret, numOfShares, threshold,fieldsize)

            # Shuffle the shares
            random.shuffle(shares)

            reconstructedSecret1 = reconstruct_secrets(shares[:threshold], 1, fieldsize)
            reconstructedSecret2 = reconstruct_secrets(shares[-threshold:], 1, fieldsize)
            isSame = secret == reconstructedSecret1 == reconstructedSecret2
            self.assertTrue(isSame)

    def test_Lagrange_basis_for_ElGamal(self):
        for i in range(100):
            secret = 3514+i
            numOfShares = 3
            threshold = 2
            fieldsize = 54287

            shares = split_secrets([secret], numOfShares, threshold, fieldsize)
            # Hardcode share for testing and debugging

            xPoints, yPoints = zip(*shares)
            basisPoly = [lagrange_For_ElGamal(xPoints, i, threshold, fieldsize) for i in range(threshold)]

            res = 0
            for i in range(threshold):
                res = (res + yPoints[i] * basisPoly[i]) % fieldsize
            isSame = res == secret
            self.assertTrue(isSame)
            self.assertEqual(res, secret)

    def test_wrap_around(self):
        secrets = [4,0]
        threshold = 9
        numOfShares = 10
        fieldsize = 11
        sharedNeeded = len(secrets) + threshold - 1

        shares = split_secrets(secrets, numOfShares, threshold, fieldsize)
        #Reconstruct the secrets
        reconstructedSecret = reconstruct_secrets(shares[:sharedNeeded], len(secrets), fieldsize)
        isSame = secrets == reconstructedSecret
        self.assertTrue(isSame)



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
    print("Errors:   ", len(result.errors))
    print("Failures: ", len(result.failures))
    print("Skipped:  ", len(result.skipped))
    print("Success:  ", result.wasSuccessful())
    print("\n")
