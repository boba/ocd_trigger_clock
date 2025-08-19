import shutil
import numpy as np
import random
from mapping_utils import set_mapping, zero, one

def generate_skewed_distribution(count, mean, percent_above_mean):
    """
    Generates a list of numbers between 0 and 1 with a specified mean and
    percentage of values above the mean, using a triangular distribution.
    """
    distribution = []
    num_above = int(count * percent_above_mean)
    num_below = count - num_above

    # Generate values for the portion above the mean (right skewed towards 1)
    for _ in range(num_above):
        # Adjust 'mode' to be higher for values intended to be above the mean
        distribution.append(random.triangular(0, 1, 0.75 + (random.random() * 0.25))) 

    # Generate values for the portion below the mean (left skewed towards 0)
    for _ in range(num_below):
        # Adjust 'mode' to be lower for values intended to be below the mean
        distribution.append(random.triangular(0, 1, 0.25 - (random.random() * 0.25))) 

    # Adjust the values to achieve the exact mean
    current_mean = sum(distribution) / len(distribution)
    scaling_factor = mean / current_mean
    distribution = [x * scaling_factor for x in distribution]

    # Clip values to ensure they stay within the 0 to 1 range after scaling
    distribution = [max(0, min(1, x)) for x in distribution]

    return distribution

def create_mapping(count=100, mean=0.5, above=0.70, mapping_file=None):
    print(f"Generating mapping with {count} entries, mean {mean}, {above*100}% above mean")
 
    # Generate 100 numbers with mean 0.5 and 70% above the mean
    my_distribution = generate_skewed_distribution(count, mean, above)
    my_distribution.sort()

    mapping = []
    y = 0
    total = 0
    for v in my_distribution:
        total += round(v,6)
        mapping.append([round(v, 6), y/100])
        y += 1    

    if mapping_file is not None:
        print(f"Writing mapping to '{mapping_file}'")
        with open(mapping_file, 'w') as f:
            for a, b in mapping:
                f.write(f"{a},{b}\n")
    # else:
    #     for a,b in mapping:
    #         print(f"[{a}, {b}]")

    print(f"")
    print(f"Generated {len(mapping)} entries in the mapping.")
    print(f"Length: {len(mapping)}")
    print(f"Mean: {total / len(mapping):.2f}")
    above_mean_count = sum(1 for x,y in mapping if x > 0.5)
    print(f"Percentage above mean: {above_mean_count / len(mapping) * 100:.2f}%")
    
    return mapping

def test_mapping(mapping, iterations = 9999):
    
    print(f"Testing mapping with {iterations} iterations")
        
    accumulator = 0
    err_zero = 0
    err_one = 0
    err_mark = 0
    total_time = 0
    
    set_mapping(mapping)
    
    for s in range(0, iterations):
        total_zero = 0
        total_one = 0
        
        total_t = 0
        skew = 0.0
        
        for i in range(0,60):
            if random.random() < .5:
                val = zero(skew)
                total_zero += val
                total_t += val
            else:
                val = one(skew)
                total_one += val
                total_t += val
            skew = total_t - (1 + i)
            # print(f"Val {val:>4.2f}  Time: {total_t:>4.2f}  Skew: {skew:>4.2f} / {i} iteration  {i+1:>2d}")
            
        total_time += total_zero + total_one             
        # print(f"totals: 0: {total_zero:>4.2f}  1: {total_one:>4.2f}  total: { total_zero + total_one:>4.2f} / {s} iteration")

    avg_time = total_time / iterations
    
    print(f"Total Time: {total_time:>9.2f} Average Time: {avg_time:>4.2f} / {iterations} iterations")    
    return total_time, avg_time

def main():
    # mapping = create_mapping(count=100, mean=0.5, above=0.70)
    # test_mapping(mapping, 99999)

    total_tests = 0
    best_mean = 0.0
    best_above = 0.0
    best_avg = 0.0
    
    num_mappings = 100
    iterations = 999
    m_range = np.arange(0.1, 0.9, 0.05)
    a_range = np.arange(0.1, 0.9, 0.05)

    for mean in m_range:
        for above in a_range:
            total_tests += 1
            mapping = create_mapping(count=num_mappings, mean=mean, above=above, mapping_file='test.csv')
            tot, avg = test_mapping(mapping, iterations=iterations)
            print(f"Test {total_tests}, Mean: {mean:.2f}, Above: {above:.2f}, Avg Time: {avg:.2f}")
            if avg > best_avg:
                best_avg = avg
                best_mean = mean
                best_above = above
                # copy mapping file to a new file
                shutil.copy('test.csv', f'test_best.csv')

            print(f"")

    print(f"Total Tests: {total_tests}, Best Mean: {best_mean:.2f}, Best Above: {best_above:.2f}, Best Avg Time: {best_avg:.2f}")
    
if __name__ == "__main__":
    main()
