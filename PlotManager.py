import matplotlib.pyplot as plt
import copy
from HillChart import HillChart

class PlotManager:
    def __init__(self, datapath, n_contours):
        self.datapath = datapath
        self.n_contours = n_contours

    def plot_3d_hill_chart(self, hill_values):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')
        hill_values.plot_hill_chart(ax=ax1)
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)
        raw_data.plot_3d_scatter(ax=ax1)
        plt.show(block=False)

    def plot_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_nD = copy.deepcopy(hill_values)
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))
        hill_values.plot_hill_chart_contour(ax=ax2[0], n_contours=self.n_contours, data_type='default')
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        hill_values_nD.plot_hill_chart_contour(ax=ax2[1], n_contours=self.n_contours, data_type='nD')
        plt.tight_layout()
        plt.show(block=False)

    def plot_normalized_hill_chart_contour(self, hill_values, BEP_data):
        hill_values_norm = copy.deepcopy(hill_values)
        hill_values_norm.normalize_efficiency(BEP_data.efficiency)
        hill_values_norm.normalize_Q11(BEP_data.Q11)
        hill_values_norm.normalize_n11(BEP_data.n11)
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))
        hill_values.plot_hill_chart_contour(ax=ax2[0], n_contours=self.n_contours, data_type='default')
        hill_values_norm.plot_hill_chart_contour(ax=ax2[1], n_contours=self.n_contours, data_type='normalized')
        plt.tight_layout()
        plt.show(block=False)

    def plot_curve_slices(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))
        q_curve_values = copy.deepcopy(hill_values)
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0, 0])
        q_curve_values.plot_power_vs_Q(ax=ax3[1, 0])

        n_curve_values = copy.deepcopy(hill_values)
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0, 1])
        n_curve_values.plot_power_vs_n(ax=ax3[1, 1])

        plt.show(block=False)

    def plot_normalized_curve_slices(self, hill_values, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))
        q_curve_values = copy.deepcopy(hill_values)
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])
        q_curve_values.normalize_efficiency(BEP_data.efficiency)
        q_curve_values.normalize_Q(BEP_data.Q)
        q_curve_values.normalize_power(BEP_data.power)
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0, 0], labels='normalized')
        q_curve_values.plot_power_vs_Q(ax=ax3[1, 0], labels='normalized')

        n_curve_values = copy.deepcopy(hill_values)
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.normalize_efficiency(BEP_data.efficiency)
        n_curve_values.normalize_n(BEP_data.n)
        n_curve_values.normalize_power(BEP_data.power)
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0, 1], labels='normalized')
        n_curve_values.plot_power_vs_n(ax=ax3[1, 1], labels='normalized')

        plt.show(block=False)
