#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：cse6140 
@File    ：draw_plot.py
@Author  ：Jiawei
@Date    ：11/28/21 9:06 AM 
'''

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import glob
import os


def read_trace(path, instance, alg):
    print(f'path = {path}')
    if instance == 'berlin52':
        solution_instance = 'Berlin'
    else:
        solution_instance = instance

    output_files = glob.glob(path + f'/{instance}_{alg}*.trace')
    print(f'length of files = {len(output_files)}')
    opt = optimal_solution.at[solution_instance, 'Value']
    all_data = []
    for file in output_files:
        trace_data = pd.read_csv(file, names=['time', 'shortest_distance'])
        trace_data['quality'] = trace_data['shortest_distance'] / opt - 1
        all_data.append(trace_data)
    print(f'length = {len(all_data)}')
    return all_data


def draw_boxplot(all_data, selected_q, instance, alg):
    runtimes = []
    for i in range(len(selected_q)):
        # append an empty list to keep runtime for a selected q
        runtimes.append([])
        for trace_data in all_data:
            df = trace_data.loc[trace_data['quality'] < selected_q[i]]
            if not df.empty:
                runtime = df.iat[0, 0]
                runtimes[i].append(runtime)

    fig, ax = plt.subplots()
    labels = ['q={}'.format(q) for q in selected_q]
    ax.boxplot(runtimes, labels=labels)
    ax.set_title(f'Boxplot for {alg} on {instance}')
    plt.ylabel('Time(s)')
    plt.style.use('fivethirtyeight')
    plt.tight_layout()
    plt.savefig(f'../output/figure/Boxplot_for_{alg}_on_{instance}')
    # plt.show()
    plt.close()


def draw_QRTD(data, selected_q, instance, alg):
    # generate xAxis data
    print(instance)
    max_times = []
    for i in range(len(data)):
        max_times.append(data[i]['time'].max())
    max_time = sorted(max_times, reverse=True)[0]
    time_points = np.arange(0, max_time, max_time/100)
    # Generate yAxis data
    prob = []
    for i in range(len(selected_q)):
        prob.append({'q': selected_q[i], 'probabilities': []})
        for time_point in time_points:
            satisfied = 0
            for trace_data in all_data:
                satisfied_records = trace_data.loc[
                    (trace_data['time'] < time_point) & (trace_data['quality'] < prob[i]['q'])]
                if satisfied_records.shape[0]:
                    satisfied += 1
            prob[i]['probabilities'].append(satisfied / len(all_data))

    # Draw plot
    fig, ax = plt.subplots()
    for i in range(len(selected_q)):
        ax.plot(time_points, prob[i]['probabilities'], label='q={}'.format(prob[i]['q']))
    plt.legend()
    ax.set_xlabel('Time(s)')
    ax.set_ylabel('P(Solve)')
    plt.style.use('fivethirtyeight')
    ax.set_title('QRTD for {} on {}'.format(alg, instance))
    plt.tight_layout()
    fig.savefig(f'../output/figure/QRTD_for_{alg}_on_{instance}.png')
    # plt.show()
    plt.close()

def draw_SQD(data, selected_t, instance, alg):
    # generate xAxis data
    max_quality = 0
    for i in range(len(data)):
        max_quality = max(data[i]['quality'].max(), max_quality)

    quality_points = np.arange(0, max_quality, max_quality / 100)

    # Generate yAxis data
    prob = []
    for i in range(len(selected_t)):
        prob.append({'t': selected_t[i], 'probabilities': []})
        for point in quality_points:
            satisfied = 0
            for trace_data in all_data:
                satisfied_records = trace_data.loc[
                    (trace_data['time'] < prob[i]['t']) & (trace_data['quality'] < point)]
                if satisfied_records.shape[0]:
                    satisfied += 1
            prob[i]['probabilities'].append(satisfied / len(all_data))

    # Draw plot
    fig, ax = plt.subplots()
    for i in range(len(selected_t)):
        ax.plot(quality_points, prob[i]['probabilities'], label='t={}'.format(prob[i]['t']))
    plt.legend()
    ax.set_xlabel('Quality')
    ax.set_ylabel('P(Solve)')
    plt.style.use('fivethirtyeight')
    ax.set_title('SQD for {} on {}'.format(alg, instance))
    plt.tight_layout()
    fig.savefig(f'../output/figure/SQD_for_{alg}_on_{instance}.png')
    # plt.show()
    plt.close()


# Read Solution
optimal_solution = pd.read_csv('../DATA/solutions.csv', index_col=0)

# for alg in ['LS1', 'LS2']:
#     for instance in ["Atlanta", "berlin52", "Boston", "Champaign", "Cincinnati", "Denver",
#                      "NYC", "Philadelphia", "Roanoke", "SanFrancisco", "Toronto", "UKansasState", "UMissouri"]:
for alg in ['LS2', 'LS1']:
    for instance in ["berlin52", "Champaign", "Denver", "NYC", "Roanoke", "SanFrancisco", "Toronto", "UMissouri"]:

        # Select instance and algorithm
        selected_instance = instance
        selected_alg = alg

        output_path = '../output/plot_data'

        all_data = read_trace(output_path, selected_instance, selected_alg)

        selected_q_QRTD =[0.1, 0.15, 0.2, 0.25]
        selected_t = [0.5, 1, 2]
        selected_q_boxplot = [0.1, 0.15]

        draw_QRTD(all_data, selected_q_QRTD, instance=selected_instance, alg=selected_alg)
        draw_SQD(all_data, selected_t, instance=selected_instance, alg=selected_alg)
        draw_boxplot(all_data, selected_q_boxplot, instance=selected_instance, alg=selected_alg)