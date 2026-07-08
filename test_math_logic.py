from questions import check_answer

def run_tests():
    print("Running math check_answer tests...")
    
    # Test Stage 1 Question 1 (Expected: 1,3,5)
    assert check_answer("s1_q1", "1,3,5") == True
    assert check_answer("s1_q1", "1, 3, 5") == True
    assert check_answer("s1_q1", "{1, 3, 5}") == True
    assert check_answer("s1_q1", "3, 1, 5") == True  # Order independence check
    assert check_answer("s1_q1", "1,2,3") == False
    print("  s1_q1 tests passed!")

    # Test Stage 1 Question 2 (Expected: -4,0,8)
    assert check_answer("s1_q2", "-4,0,8") == True
    assert check_answer("s1_q2", "-4, 0, 8") == True
    assert check_answer("s1_q2", "0, 8, -4") == True
    assert check_answer("s1_q2", "-4, 0, 0, 8") == True  # Handles duplicate inputs correctly
    assert check_answer("s1_q2", "8, 0, -4") == True
    print("  s1_q2 tests passed!")

    # Test Stage 2 Question 2 (Interval notation)
    assert check_answer("s2_q2", "[-3,4]") == True
    assert check_answer("s2_q2", "[-3, 4]") == True
    assert check_answer("s2_q2", "-3 <= x <= 4") == True
    assert check_answer("s2_q2", "-3<=x<=4") == True
    assert check_answer("s2_q2", "(-3,4)") == False  # Wrong parenthesis type
    print("  s2_q2 (interval) tests passed!")

    # Test Stage 3 Question 1 (Algebraic domain limit)
    assert check_answer("s3_q1", "x != 3") == True
    assert check_answer("s3_q1", "x!=3") == True
    assert check_answer("s3_q1", "R - {3}") == True
    assert check_answer("s3_q1", "x != 4") == False
    print("  s3_q1 (inequality) tests passed!")

    # Test Stage 3 Question 2 (Square root domain limit)
    assert check_answer("s3_q2", "x >= 2") == True
    assert check_answer("s3_q2", "x>=2") == True
    assert check_answer("s3_q2", "[2, inf)") == True
    assert check_answer("s3_q2", "[2, infinity)") == True
    print("  s3_q2 tests passed!")

    # Test Stage 3 Question 3 (Quadratic range limit)
    assert check_answer("s3_q3", "y >= 4") == True
    assert check_answer("s3_q3", "y>=4") == True
    assert check_answer("s3_q3", "f(x) >= 4") == True
    assert check_answer("s3_q3", "[4, inf)") == True
    print("  s3_q3 tests passed!")

    print("All math tests passed successfully!")

if __name__ == '__main__':
    run_tests()
