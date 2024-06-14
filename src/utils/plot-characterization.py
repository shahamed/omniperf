##############################################################################bl
# MIT License
#
# Copyright (c) 2021 - 2024 Advanced Micro Devices, Inc. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
##############################################################################el

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import plotly.graph_objects as go
import pandas as pd

plt.rcParams['figure.figsize'] = [20, 8]
plt.rcParams['font.size'] = 24

WIDTH = 0.5
COLORS = ["#2e8b57","#ffa500","#1e90ff","#0000ff","#00ff00", "#ff1493"]

def create_plots(charaterization_input: pd.DataFrame):
    data_df = charaterization_input
    plt1 = end_to_end_plt_v2(data_df)
    plt2 = gpu_bottleneck_plt_v2(data_df)
    # test other plots
    end_to_end_plt(data_df)
    gpu_bottleneck_plt(data_df)
    return plt1, plt2

def end_to_end_plt_v2(data_df):
    '''
    This portion of code will graph the end-to-end CPU/GPU timing breakdown
    '''
    fig = go.Figure()

    # iterate over the number of GPUs in the system
    for row_idx in range(data_df.shape[0]):
        base = 0
        color_idx = 0

        # for calculating cpu time, take omnitrace total trace time
        # and subtract gpu time, communication time, and cold invoke time
        # note: depending on omnitrace bugs, you may want to use 
        # omniperf's gpu runtime and/or gpu-gpu communication time
        cpu_time = data_df['ot_total_trace_time'][row_idx] - data_df['op_gpu_time'][row_idx] - \
            data_df['ot_host_device_time'][row_idx] - \
            data_df['ot_device_host_time'][row_idx] - \
            data_df['op_gpu_gpu_comm_time'][row_idx] - \
            data_df['ot_invoke_time'][row_idx]

        fig.add_trace(go.Bar(y=[row_idx], x=[cpu_time], orientation='h', marker_color=COLORS[color_idx], name='CPU'))
        base += cpu_time
        color_idx += 1

        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_host_device_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='Host To Device'))
        base += data_df['ot_host_device_time'][row_idx]
        color_idx += 1

        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_device_host_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='Device to Host'))
        base += data_df['ot_device_host_time'][row_idx]
        color_idx += 1

        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['op_gpu_gpu_comm_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='GPU-GPU'))
        base += data_df['op_gpu_gpu_comm_time'][row_idx]
        color_idx += 1

        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_invoke_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='Invoke Overhead'))
        base += data_df['ot_invoke_time'][row_idx]
        color_idx += 1

        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['op_gpu_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='GPU'))
        base += data_df['op_gpu_time'][row_idx]

    fig.update_layout(yaxis=dict(tickmode='array', tickvals=list(range(data_df.shape[0])), ticktext=[f'GPU {int(data_df["gpu_id"][idx])}' for idx in range(data_df.shape[0])]),
                      xaxis=dict(title='Runtime (ns)'),
                      title='E2E Runtime Classification: CPU, GPU, Communication',
                      barmode='stack',
                      legend=dict(
                            orientation="h",
                            yanchor="bottom",  # Anchor legend to the bottom
                            xanchor="left",  # Anchor legend to the left
                            x=0,  # Set legend x-position to 0 (leftmost)
                            y=-0.5,  # Set legend y-position slightly below the plot area 
                      ))
    return fig


def gpu_bottleneck_plt_v2(data_df):
    '''
    This portion of code will plot the GPU kernel's bottlenecks
    '''
    fig = go.Figure()

    # since we're stacking over multiple for loops, keep track of a base per GPU
    bases = [0 for _ in range(data_df.shape[0])]

    # we need 3 for loops:
    # one for the no flop time
    # one for underperforming kernels (< 80% percentage of peak threshold)
    # one for above threshold kernels (> 80% percentage of peak threshold)
    for row_idx in range(data_df.shape[0]):
        color_idx = 0

        #ax.barh(row_idx, data_df['ot_above_util_lds_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_above_util_lds_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='LDS BW'))
        bases[row_idx] += data_df['ot_above_util_lds_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_above_util_gl1_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_above_util_gl1_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='GL1 BW'))
        bases[row_idx] += data_df['ot_above_util_gl1_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_above_util_gl2_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_above_util_gl2_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='GL2 BW'))
        bases[row_idx] += data_df['ot_above_util_gl2_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_above_util_hbm_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_above_util_hbm_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='HBM BW'))
        bases[row_idx] += data_df['ot_above_util_hbm_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_above_util_valu_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_above_util_valu_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='VALU Compute'))
        bases[row_idx] += data_df['ot_above_util_valu_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_above_util_mfma_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_above_util_mfma_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], name='MFMA Compute'))
        bases[row_idx] += data_df['ot_above_util_mfma_time'][row_idx]
        color_idx += 1

        fig.add_vline(x=bases[row_idx], line_width=5.0, line_color='black')

    for row_idx in range(data_df.shape[0]):
        color_idx = 0

        #ax.barh(row_idx, data_df['ot_under_util_lds_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_under_util_lds_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='/'))
        bases[row_idx] += data_df['ot_under_util_lds_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_under_util_gl1_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_under_util_gl1_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='/'))
        bases[row_idx] += data_df['ot_under_util_gl1_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_under_util_gl2_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_under_util_gl2_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='/'))
        bases[row_idx] += data_df['ot_under_util_gl2_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_under_util_hbm_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_under_util_hbm_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='/'))
        bases[row_idx] += data_df['ot_under_util_hbm_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_under_util_valu_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_under_util_valu_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='/'))
        bases[row_idx] += data_df['ot_under_util_valu_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_under_util_mfma_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_under_util_mfma_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='/'))
        bases[row_idx] += data_df['ot_under_util_mfma_time'][row_idx]
        color_idx += 1

        fig.add_vline(x=bases[row_idx], line_width=5.0, line_color='black')

    for row_idx in range(data_df.shape[0]):
        color_idx = 0

        #ax.barh(row_idx, data_df['ot_no_flops_lds_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_no_flops_lds_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='x'))
        bases[row_idx] += data_df['ot_no_flops_lds_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_no_flops_gl1_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_no_flops_gl1_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='x'))
        bases[row_idx] += data_df['ot_no_flops_gl1_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_no_flops_gl2_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_no_flops_gl2_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='x'))
        bases[row_idx] += data_df['ot_no_flops_gl2_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_no_flops_hbm_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_no_flops_hbm_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='x'))
        bases[row_idx] += data_df['ot_no_flops_hbm_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_no_flops_valu_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_no_flops_valu_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='x'))
        bases[row_idx] += data_df['ot_no_flops_valu_time'][row_idx]
        color_idx += 1

        #ax.barh(row_idx, data_df['ot_no_flops_mfma_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        fig.add_trace(go.Bar(y=[row_idx], x=[data_df['ot_no_flops_mfma_time'][row_idx]], orientation='h', marker_color=COLORS[color_idx], showlegend=False, marker_pattern_shape='x'))
        bases[row_idx] += data_df['ot_no_flops_mfma_time'][row_idx]
        color_idx += 1

    fig.add_trace(go.Bar(x=[0], y=[0], marker_pattern_shape='', name='Above Threshold', showlegend=True, marker_color='white'))
    fig.add_trace(go.Bar(x=[0], y=[0], marker_pattern_shape='/', name='Below Threshold', showlegend=True, marker_color='white'))
    fig.add_trace(go.Bar(x=[0], y=[0], marker_pattern_shape='x', name='No FLOPs', showlegend=True, marker_color='white'))
    fig.update_layout(yaxis=dict(tickmode='array', tickvals=list(range(data_df.shape[0])), ticktext=[f'GPU {int(data_df["gpu_id"][idx])}' for idx in range(data_df.shape[0])]),
                      xaxis=dict(title='Runtime (ns)'),
                      title='GPU Kernel Runtime Breakdowns by Bottlenecks and Performance',
                      barmode='stack',
                      legend=dict(
                            orientation="h",
                            yanchor="bottom",  # Anchor legend to the bottom
                            xanchor="left",  # Anchor legend to the left
                            x=0,  # Set legend x-position to 0 (leftmost)
                            y=-0.5  # Set legend y-position slightly below the plot area
                      ))
    return fig

def end_to_end_plt(data_df):
    fig, ax = plt.subplots()
    # iterate over the number of GPUs in the system
    for row_idx in range(data_df.shape[0]):
        base = 0
        color_idx = 0
        # for calculating cpu time, take omnitrace total trace time
        # and subtract gpu time, communication time, and cold invoke time
        # note: depending on omnitrace bugs, you may want to use 
        # omniperf's gpu runtime and/or gpu-gpu communication time
        cpu_time = data_df['ot_total_trace_time'][row_idx] - \
            data_df['op_gpu_time'][row_idx] - \
            data_df['ot_host_device_time'][row_idx] - \
            data_df['ot_device_host_time'][row_idx] - \
            data_df['op_gpu_gpu_comm_time'][row_idx] - \
            data_df['ot_invoke_time'][row_idx]

        ax.barh(row_idx, cpu_time, WIDTH, left=base, color=COLORS[color_idx])
        base += cpu_time
        color_idx += 1

        ax.barh(row_idx, data_df['ot_host_device_time'][row_idx], WIDTH, left=base, color=COLORS[color_idx])
        base += data_df['ot_host_device_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_device_host_time'][row_idx], WIDTH, left=base, color=COLORS[color_idx])
        base += data_df['ot_device_host_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['op_gpu_gpu_comm_time'][row_idx], WIDTH, left=base, color=COLORS[color_idx])
        base += data_df['op_gpu_gpu_comm_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_invoke_time'][row_idx], WIDTH, left=base, color=COLORS[color_idx])
        base += data_df['ot_invoke_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['op_gpu_time'][row_idx], WIDTH, left=base, color=COLORS[color_idx])
        base += data_df['op_gpu_time'][row_idx]

    plt.yticks(list(range(data_df.shape[0])), labels=[f'GPU {data_df["gpu_id"][idx]}' for idx in range(data_df.shape[0])])
    plt.ylabel('GPU ID')
    plt.xlabel('Runtime (ns)')
    plt.title('E2E Runtime Classification: CPU, GPU, Communication')
    legend_labels = ['CPU', 'Host To Device', 'Device to Host', 'GPU-GPU', 'Invoke Overhead', 'GPU']
    ax.legend(handles=[mpatches.Patch(color=COLORS[i], label=legend_labels[i]) for i in range(len(legend_labels))])

    plt.savefig('sample_output' + '-e2e_time.pdf', bbox_inches='tight')

def gpu_bottleneck_plt(data_df):
    fig, ax = plt.subplots()
    # since we're stacking over multiple for loops, keep track of a base per GPU
    bases = [0 for _ in range(data_df.shape[0])]

    # we need 3 for loops:
    # one for the no flop time
    # one for underperforming kernels (< 80% percentage of peak threshold)
    # one for above threshold kernels (> 80% percentage of peak threshold)
    for row_idx in range(data_df.shape[0]):
        color_idx = 0

        ax.barh(row_idx, data_df['ot_above_util_lds_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        bases[row_idx] += data_df['ot_above_util_lds_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_above_util_gl1_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        bases[row_idx] += data_df['ot_above_util_gl1_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_above_util_gl2_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        bases[row_idx] += data_df['ot_above_util_gl2_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_above_util_hbm_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        bases[row_idx] += data_df['ot_above_util_hbm_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_above_util_valu_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        bases[row_idx] += data_df['ot_above_util_valu_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_above_util_mfma_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx])
        bases[row_idx] += data_df['ot_above_util_mfma_time'][row_idx]
        color_idx += 1

        plt.vlines(bases[row_idx], ymin=row_idx-0.4, ymax=row_idx+0.4, colors='black', linewidth=5.0)

    for row_idx in range(data_df.shape[0]):
        color_idx = 0

        ax.barh(row_idx, data_df['ot_under_util_lds_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        bases[row_idx] += data_df['ot_under_util_lds_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_under_util_gl1_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        bases[row_idx] += data_df['ot_under_util_gl1_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_under_util_gl2_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        bases[row_idx] += data_df['ot_under_util_gl2_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_under_util_hbm_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        bases[row_idx] += data_df['ot_under_util_hbm_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_under_util_valu_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        bases[row_idx] += data_df['ot_under_util_valu_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_under_util_mfma_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='/')
        bases[row_idx] += data_df['ot_under_util_mfma_time'][row_idx]
        color_idx += 1

        plt.vlines(bases[row_idx], ymin=row_idx-0.4, ymax=row_idx+0.4, colors='black', linewidth=5.0)

    for row_idx in range(data_df.shape[0]):
        color_idx = 0

        ax.barh(row_idx, data_df['ot_no_flops_lds_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        bases[row_idx] += data_df['ot_no_flops_lds_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_no_flops_gl1_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        bases[row_idx] += data_df['ot_no_flops_gl1_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_no_flops_gl2_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        bases[row_idx] += data_df['ot_no_flops_gl2_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_no_flops_hbm_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        bases[row_idx] += data_df['ot_no_flops_hbm_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_no_flops_valu_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        bases[row_idx] += data_df['ot_no_flops_valu_time'][row_idx]
        color_idx += 1

        ax.barh(row_idx, data_df['ot_no_flops_mfma_time'][row_idx], WIDTH, left=bases[row_idx], color=COLORS[color_idx], hatch='X')
        bases[row_idx] += data_df['ot_no_flops_mfma_time'][row_idx]
        color_idx += 1

    plt.yticks(list(range(data_df.shape[0])), labels=[f'GPU {data_df["gpu_id"][idx]}' for idx in range(data_df.shape[0])])
    plt.ylabel('GPU ID')
    plt.xlabel('Runtime (ns)')
    plt.title('GPU Kernel Runtime Breakdowns by Bottlenecks and Performance')

    # Had to create the legend manually so as to include the / and X hatch marks.
    legend_LDS = mpatches.Patch(color=COLORS[0], label='LDS BW')
    legend_GL1 = mpatches.Patch(color=COLORS[1], label='GL1 BW')
    legend_GL2 = mpatches.Patch(color=COLORS[2], label='GL2 BW')
    legend_HBM = mpatches.Patch(color=COLORS[3], label='HBM BW')
    legend_VALU = mpatches.Patch(color=COLORS[4], label='VALU Compute')
    legend_MFMA = mpatches.Patch(color=COLORS[5], label='MFMA Compute')
    legend_blank = mpatches.Patch(facecolor='white', edgecolor='black', label='Above Threshold')
    legend_slash = mpatches.Patch(facecolor='white', edgecolor='black', hatch='/', label='Below Threshold')
    legend_Xmark = mpatches.Patch(facecolor='white', edgecolor='black', hatch='X', label='No FLOPs')
    ax.legend(handles=[legend_LDS, legend_GL1, legend_GL2, legend_HBM, legend_VALU, legend_MFMA, legend_blank, legend_slash, legend_Xmark], loc='best')

    plt.savefig('sample_output' + '-gpu_time.pdf', bbox_inches='tight')