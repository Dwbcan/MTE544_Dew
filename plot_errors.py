import matplotlib.pyplot as plt
from utilities import FileReader

def get_controller_type(filename):
    if '_p.' in filename.lower():
        return "P Controller"
    elif '_pid.' in filename.lower():
        return "PID Controller"
    elif '_parabola.' in filename.lower():
        return "Parabola Trajectory"
    elif '_sigmoid.' in filename.lower():
        return "Sigmoid Trajectory"
    return "Controller"

def plot_errors(filename):
    
    headers, values=FileReader(filename).read_file()
    
    time_list=[]
    
    first_stamp=values[0][-1]
    
    for val in values:
        time_list.append(val[-1] - first_stamp)

    fig = plt.figure(figsize=(15,10))
    gs = plt.GridSpec(3, 2, figure=fig, width_ratios=[1, 1])
    
    ax1 = fig.add_subplot(gs[:, 0])
    ax1.plot([lin[0] for lin in values], [lin[1] for lin in values])
    controller_type = get_controller_type(filename)
    ax1.set_title(f"Linear Error Phase Plot\n({controller_type})")
    ax1.set_xlabel("e_linear (m)")
    ax1.set_ylabel("e_dot_linear (m/s)")
    ax1.grid(True)

    # Error
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(time_list, [lin[0] for lin in values], 'b-')
    ax2.set_title("Linear Error")
    ax2.set_ylabel("e_linear (m)")
    ax2.grid(True)
    ax2.set_xticklabels([])

    # Error derivative
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(time_list, [lin[1] for lin in values], 'orange')
    ax3.set_title("Linear Error Derivative")
    ax3.set_ylabel("e_dot_linear (m/s)")
    ax3.grid(True)
    ax3.set_xticklabels([])

    # Error integral
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.plot(time_list, [lin[2] for lin in values], 'g-')
    ax4.set_title("Linear Error Integral")
    ax4.set_xlabel("Time (nanoseconds)")
    ax4.set_ylabel("e_int_linear (m·s)")
    ax4.grid(True)

    plt.tight_layout()
    plt.show()
    
    





import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    
    args = parser.parse_args()
    
    print("plotting the files", args.files)

    filenames=args.files
    for filename in filenames:
        plot_errors(filename)



