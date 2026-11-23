import argparse
import bisect
from collections import Counter
import json
from math import gcd, isqrt
from pathlib import Path


def smooth_numbers(limit):
    numbers = []
    power_two = 1
    while power_two <= limit:
        power_three = 1
        while power_two * power_three <= limit:
            numbers.append(power_two * power_three)
            power_three *= 3
        power_two *= 2
    return sorted(numbers)


def smooth_part(number):
    remainder = number
    for prime in (2, 3):
        while remainder % prime == 0:
            remainder //= prime
    return number // remainder, remainder


def mobius_values(limit):
    values = [1] * (limit + 1)
    is_prime = [True] * (limit + 1)
    is_prime[:2] = [False, False]
    primes = []
    for prime in range(2, limit + 1):
        if not is_prime[prime]:
            continue
        primes.append(prime)
        for multiple in range(prime, limit + 1, prime):
            values[multiple] *= -1
            if multiple > prime:
                is_prime[multiple] = False
        for multiple in range(prime * prime, limit + 1, prime * prime):
            values[multiple] = 0
    values[0] = 0
    return values, primes


def inverse(function):
    limit = len(function) - 1
    assert function[1] == 1
    answer = [0] * (limit + 1)
    partial = [0] * (limit + 1)
    for divisor in range(1, limit + 1):
        answer[divisor] = 1 if divisor == 1 else -partial[divisor]
        for multiple in range(2 * divisor, limit + 1, divisor):
            partial[multiple] += answer[divisor] * function[multiple // divisor]
    return answer


def convolution_at(function, other, number):
    total = 0
    for divisor in range(1, isqrt(number) + 1):
        if number % divisor:
            continue
        quotient = number // divisor
        total += function[divisor] * other[quotient]
        if quotient != divisor:
            total += function[quotient] * other[divisor]
    return total


def rational_rank(two_exponent, three_exponent):
    weight = 2 * two_exponent + 3 * three_exponent
    return 1 + sum(
        1
        for other_three in range(weight // 3 + 1)
        for other_two in range(weight // 2 + 1)
        if 2 * other_two + 3 * other_three < weight
        or (2 * other_two + 3 * other_three == weight and other_three < three_exponent)
    )


def binary_value(number):
    return (number // (number & -number) + 1) // 2


def divisors(number):
    lower = []
    upper = []
    for divisor in range(1, isqrt(number) + 1):
        if number % divisor == 0:
            lower.append(divisor)
            if divisor * divisor != number:
                upper.append(number // divisor)
    return lower + upper[::-1]


def binary_counterexample():
    number = 72747675
    sparse_inverse = {}
    for divisor in divisors(number):
        sparse_inverse[divisor] = 1 if divisor == 1 else -sum(
            binary_value(factor) * sparse_inverse[divisor // factor]
            for factor in divisors(divisor) if factor > 1
        )
    convolution = sum(binary_value(divisor) * sparse_inverse[number // divisor] for divisor in divisors(number))
    assert convolution == 0
    value = binary_value(number) + sparse_inverse[number]
    assert value == -14126242
    return {'n': number, 'A003602': binary_value(number), 'A349134': sparse_inverse[number],
            'A349135': value, 'convolution': convolution, 'divisors': len(sparse_inverse)}


def run(limit):
    assert 25000 <= limit <= 100000
    smooth = smooth_numbers(limit)
    ranks = {number: index for index, number in enumerate(smooth, 1)}
    function = [0] * (limit + 1)
    labels = {}
    frequencies = Counter()
    core_frequencies = Counter()
    records = []
    maximum = 0
    for number in range(1, limit + 1):
        core, complement = smooth_part(number)
        function[number] = bisect.bisect_right(smooth, core)
        if core not in labels:
            labels[core] = len(labels) + 1
        assert labels[core] == function[number] == ranks[core]
        frequencies[complement] += 1
        assert frequencies[complement] == function[number]
        core_frequencies[core] += 1
        complement_rank = 2 * (complement // 6) + 1 + (complement % 6 == 5)
        assert core_frequencies[core] == complement_rank
        if function[number] > maximum:
            records.append(number)
            maximum = function[number]
    assert records == smooth
    inverse_values = inverse(function)
    convolution_cases = min(limit, 5000)
    for number in range(1, convolution_cases + 1):
        assert convolution_at(function, inverse_values, number) == (number == 1)
    mobius, primes = mobius_values(limit)
    for number in range(1, limit + 1):
        core, complement = smooth_part(number)
        assert inverse_values[number] == inverse_values[core] * mobius[complement]
    square_cases = 0
    sign_cases = 0
    for prime in primes:
        if prime <= 3:
            continue
        for number in range(prime * prime, limit + 1, prime * prime):
            assert inverse_values[number] == 0
            square_cases += 1
        for number in range(1, limit // prime + 1):
            if number % prime:
                assert inverse_values[prime * number] == -inverse_values[number]
                sign_cases += 1
    target_cases = limit // 25
    for number in range(1, target_cases + 1):
        assert function[number] == function[25 * number] + inverse_values[25 * number]
    multiplier_cases = 0
    for multiplier in range(1, 1001):
        if gcd(multiplier, 6) != 1:
            assert function[25 * multiplier] + inverse_values[25 * multiplier] != function[25]
            continue
        if mobius[multiplier]:
            assert function[multiplier] + inverse_values[multiplier] != function[1]
        else:
            for number in range(1, min(100, limit // multiplier) + 1):
                assert function[multiplier * number] + inverse_values[multiplier * number] == function[number]
                multiplier_cases += 1
    complement_values = [0] * (limit + 1)
    for number in range(1, limit + 1):
        core, complement = smooth_part(number)
        complement_values[number] = 2 * (complement // 6) + 1 + (complement % 6 == 5)
    complement_inverse = inverse(complement_values)
    dual_sum = [left + right for left, right in zip(complement_values, complement_inverse)]
    for number in range(1, convolution_cases + 1):
        assert convolution_at(complement_values, complement_inverse, number) == (number == 1)
    positivity_cases = 0
    for number in range(1, limit + 1):
        core, complement = smooth_part(number)
        assert complement_inverse[number] == mobius[core] * complement_inverse[complement]
        if number % 4 == 0 or number % 9 == 0:
            assert dual_sum[number] == complement_values[number] > 0
            positivity_cases += 1
        if number <= limit // 4:
            assert dual_sum[4 * number] == complement_values[number]
        if number <= limit // 9:
            assert dual_sum[9 * number] == complement_values[number]
    dual_multiplier_cases = 0
    for multiplier in range(1, 1001):
        core, complement = smooth_part(multiplier)
        valid = complement == 1 and (multiplier % 4 == 0 or multiplier % 9 == 0)
        if valid:
            for number in range(1, min(100, limit // multiplier) + 1):
                assert dual_sum[multiplier * number] == complement_values[number]
                dual_multiplier_cases += 1
        else:
            witness = 4 if complement > 1 else 1
            assert dual_sum[multiplier * witness] != complement_values[witness]
    binary_values = [0] + [binary_value(number) for number in range(1, limit + 1)]
    binary_inverse = inverse(binary_values)
    binary_sum = [left + right for left, right in zip(binary_values, binary_inverse)]
    ruler_values = [0] + [(number & -number).bit_length() for number in range(1, limit + 1)]
    ruler_inverse = inverse(ruler_values)
    ruler_sum = [left + right for left, right in zip(ruler_values, ruler_inverse)]
    for number in range(1, limit + 1):
        assert ruler_inverse[number] == mobius[number] - (mobius[number // 2] if number % 2 == 0 else 0)
        if number <= convolution_cases:
            assert convolution_at(binary_values, binary_inverse, number) == (number == 1)
            assert convolution_at(ruler_values, ruler_inverse, number) == (number == 1)
    binary_multiplier_cases = 0
    ruler_multiplier_cases = 0
    for multiplier in range(1, 1001):
        binary_valid = multiplier & (multiplier - 1) == 0 and multiplier >= 4
        ruler_valid = multiplier % 2 == 1 and mobius[multiplier] == 0
        if binary_valid:
            for number in range(1, min(100, limit // multiplier) + 1):
                assert binary_sum[multiplier * number] == binary_values[number]
                binary_multiplier_cases += 1
        else:
            witness = 4 if binary_value(multiplier) > 1 else 1
            assert binary_sum[multiplier * witness] != binary_values[witness]
        if ruler_valid:
            for number in range(1, min(100, limit // multiplier) + 1):
                assert ruler_sum[multiplier * number] == ruler_values[number]
                ruler_multiplier_cases += 1
        else:
            witness = 9 if multiplier % 2 == 0 else 1
            assert ruler_sum[multiplier * witness] != ruler_values[witness]
    prefixes = json.loads(Path(__file__).with_name('oeis-prefixes.json').read_text())
    tested_prefixes = {}
    values = {'A322026': function, 'A323883': inverse_values,
              'A323884': [left + right for left, right in zip(function, inverse_values)],
              'A323881': complement_inverse, 'A323882': dual_sum,
              'A349134': binary_inverse, 'A349135': binary_sum,
              'A001511': ruler_values, 'A092673': ruler_inverse, 'A323885': ruler_sum}
    for identifier, expected in prefixes['sequences'].items():
        if identifier not in values:
            continue
        assert values[identifier][1:len(expected) + 1] == expected
        tested_prefixes[identifier] = len(expected)
    array_values = {'A247714': [], 'A255975': [], 'A087465': []}
    array_smooth = smooth_numbers(3 ** 12)
    for diagonal in range(12):
        for three_exponent in range(diagonal + 1):
            two_exponent = diagonal - three_exponent
            array_values['A247714'].append(bisect.bisect_right(array_smooth, 2 ** two_exponent * 3 ** three_exponent))
            array_values['A255975'].append(bisect.bisect_right(array_smooth, 2 ** three_exponent * 3 ** two_exponent))
            array_values['A087465'].append(rational_rank(two_exponent, three_exponent))
    for identifier, calculated in array_values.items():
        expected = prefixes['sequences'][identifier]
        assert calculated[:len(expected)] == expected
        tested_prefixes[identifier] = len(expected)
    assert array_values['A247714'][35] == 49
    assert array_values['A087465'][35] == 48
    elementary_limit = 2000
    mobius_count = [0] * (elementary_limit + 1)
    for divisor in range(1, elementary_limit + 1):
        coefficient = mobius[divisor] if gcd(divisor, 6) == 1 else 0
        for number in range(divisor, elementary_limit + 1, divisor):
            mobius_count[number] += coefficient
    floor_difference_count = 0
    cumulative_mobius_count = 0
    for number in range(1, elementary_limit + 1):
        actual_count = bisect.bisect_right(smooth, number)
        cumulative_mobius_count += mobius_count[number]
        assert cumulative_mobius_count == actual_count
        core, complement = smooth_part(number)
        assert gcd(number, pow(6, number, number)) == core
        power = 6 ** number
        floor_difference_count += power // number - (power - 1) // number
        assert floor_difference_count == actual_count
    example_cases = []
    for prime in (2, 3, 5, 7):
        example = [0] * 513
        for number in range(1, len(example)):
            base = number
            while base % prime == 0:
                base //= prime
            example[number] = 1 if base == 1 else ((base * base + 3 * base) % 11) - 5
        example_inverse = inverse(example)
        for number in range(1, len(example)):
            assert convolution_at(example, example_inverse, number) == (number == 1)
            if number % (prime * prime) == 0:
                assert example_inverse[number] == 0
            if number % prime == 0 and number % (prime * prime):
                assert example_inverse[number] == -example_inverse[number // prime]
        example_cases.append({'prime': prime, 'indices': 512})
    return {
        'status': 'pass',
        'arithmetic': 'exact integers',
        'rank_and_restricted_growth_indices': limit,
        'counting_formula_indices': limit,
        'mutual_ordinal_transform_indices': limit,
        'record_positions_compared': len(smooth),
        'inverse_convolution_indices': convolution_cases,
        'inverse_factorization_indices': limit,
        'prime_square_vanishing_cases': square_cases,
        'prime_sign_cases': sign_cases,
        'target_identity_indices': {'first': 1, 'last': target_cases},
        'multiplier_range': {'first': 1, 'last': 1000},
        'nonsquarefree_multiplier_identity_cases': multiplier_cases,
        'dual_factorization_indices': limit,
        'dual_inverse_convolution_indices': convolution_cases,
        'dual_four_identity_indices': limit // 4,
        'dual_nine_identity_indices': limit // 9,
        'dual_positive_square_indices': positivity_cases,
        'dual_multiplier_identity_cases': dual_multiplier_cases,
        'binary_multiplier_identity_cases': binary_multiplier_cases,
        'ruler_multiplier_identity_cases': ruler_multiplier_cases,
        'binary_nonnegativity_prior_counterexample': binary_counterexample(),
        'rank_array_counterexample': {'zero_based_position': 35, 'A247714': 49, 'A087465': 48},
        'elementary_smooth_count_and_gcd_indices': elementary_limit,
        'published_prefix_lengths': tested_prefixes,
        'general_support_examples': example_cases,
        'proof_scope': 'Finite comparisons supplement the written all-index proofs in note.tex.',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=50000)
    parser.add_argument('--output', type=Path)
    arguments = parser.parse_args()
    result = json.dumps(run(arguments.limit), indent=2, sort_keys=True) + '\n'
    if arguments.output:
        arguments.output.write_text(result)
    print(result, end='')


if __name__ == '__main__':
    main()
