import os
import subprocess
import csv
import matplotlib.pyplot as plt
import argparse

def clean_page_cache():
    # cmd = "sudo /scratch/pixels-external/drop_cache.sh"
    cmd = "sudo bash -c \"sync; echo 3 > /proc/sys/vm/drop_caches\""
    if verbose:
        print(cmd)
    os.system(cmd)

def run_benchmark(benchmark_path, draw=0):
    # Ensure the path is a directory
    if not os.path.isdir(benchmark_path):
        print(f"Error: {benchmark_path} is not a valid directory")
        return

    # Get the last part of the directory name for the output file
    # Get the last two parts of the directory name for the output file
    path_parts = os.path.normpath(benchmark_path).split(os.sep)
    output_name = f"{path_parts[-2]}_{path_parts[-1]}"
    output_csv = "output/"+f"{output_name}.csv"

    results = []

    # Traverse all files in the directory
    for root, dirs, files in os.walk(benchmark_path):

        files = sorted([file for file in files if file.endswith('.benchmark')],
                       key=lambda x: int(x[1:3]))
        print(files)
        for file in files:
            if file.endswith('.benchmark'):
                # Construct the full file path
                benchmark_file = os.path.join(root, file)

                # Run the command and capture output
                try:
                    cmd=os.path.join(pixels_home,"cpp/build/release/benchmark/benchmark_runner")+" \""+benchmark_file+"\""
                    if verbose:
                        print(cmd)
                    output=subprocess.getoutput(cmd)

                    # print(output)
                    # Find the result in the output
                    for line in output.splitlines():
                        if line.startswith('Result:'):
                            time = float(line.split()[1])
                            results.append((file, time))
                            if verbose:
                                print(f"File {file} ran successfully, result: {time}")
                            break
                except Exception as e:
                    print(f"Error running {benchmark_file}: {e}")

    # Save results to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Benchmark', 'Result'])
        for file, time in results:
            writer.writerow([file, time])

    print(f"Results saved to {output_csv}")

    # Plot the results if requested
    if draw:
        plot_results(output_name, results)

def plot_results(title, results):
    # Extract filenames and times
    benchmarks = [r[0].split('.')[0] for r in results]
    times = [r[1] for r in results]

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.bar(benchmarks, times, color='skyblue')
    plt.xlabel('Benchmark')
    plt.ylabel('Result Time (s)')
    plt.title(f'Results for {title}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("output/"+f"{title}.png")
    plt.show()
    print(f"Plot saved as {title}.png")

if __name__ == "__main__":
    global pixels_home
    global verbose

    pixels_home=os.environ.get('PIXELS_SRC')
    current_dir=os.getcwd()
    os.makedirs(os.path.join(current_dir,"output"),exist_ok=True)
    # if pixels_home == None:
    #     pixels_home='/home/pixels/dev/pixels/'
    #     print("You need to set $PIXELS_HOME first.")
    # Use argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description="Run benchmarks and save results.")
    parser.add_argument('--dir', type=str, required=True, help='Directory containing benchmark files')
    parser.add_argument('--draw', type=int, default=0, choices=[0, 1], help='Draw plot: 1 for yes, 0 for no (default: 0)')
    parser.add_argument('--from-page-cache',  help='if reading file from page cache',type=int,default=0,choices=[0,1])
    parser.add_argument('--v', dest='verbose', help='output the command',type=int,default=1,choices=[0,1])
    args = parser.parse_args()

    from_page_cache=args.from_page_cache
    verbose=args.verbose
    if from_page_cache:
        pass
    else:
        clean_page_cache()

    run_benchmark(args.dir, args.draw)

