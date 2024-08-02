import matplotlib.pyplot as plt
from HillChart import HillChart

class Plotter:
    def __init__(self):
        self.datapath = None

    def prepare_core_data(self, selected_params, var1, var2):
        BEP_values = HillChart()
        BEP_values.read_hill_chart_values(self.datapath)
        
        try:
            BEP_values.filter_for_maximum_efficiency()
            BEP_values.calculate_cases(selected_params, var1, var2)
        except ValueError as e:
            raise ValueError(f"Error filtering data for maximum efficiency: {e}")

        BEP_data = BEP_values.return_values()

        hill_values = HillChart()
        hill_values.read_hill_chart_values(self.datapath)
        hill_values.prepare_hill_chart_data()

        hill_values_nD = HillChart()
        hill_values_nD.read_hill_chart_values(self.datapath)
        hill_values_nD.prepare_hill_chart_data()
        
        return BEP_data, hill_values, hill_values_nD

    def plot_3d_hill_chart(self, hill_values):
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection='3d')
        hill_values.plot_hill_chart(ax=ax1)
        raw_data = HillChart()
        raw_data.read_hill_chart_values(self.datapath)
        raw_data.plot_3d_scatter(ax=ax1)
        plt.show(block=False)

    def plot_hill_chart_contour(self, hill_values, hill_values_nD, BEP_data):
        _, ax2 = plt.subplots(1, 2, figsize=(15, 7))
        hill_values.plot_hill_chart_contour(ax=ax2[0], data_type='default')
        hill_values_nD.calculate_cases([1, 4], BEP_data.H[0], BEP_data.D[0])
        hill_values_nD.plot_hill_chart_contour(ax=ax2[1], data_type='nD')
        plt.tight_layout()
        plt.show(block=False)

    def plot_curve_slices(self, BEP_data):
        _, ax3 = plt.subplots(2, 2, figsize=(15, 10))
        q_curve_values = HillChart()
        q_curve_values.read_hill_chart_values(self.datapath)
        q_curve_values.prepare_hill_chart_data()
        q_curve_values.slice_hill_chart_data(selected_n11=BEP_data.n11[0], selected_Q11=None)
        q_curve_values.calculate_cases([3, 4], BEP_data.n[0], BEP_data.D[0])
        q_curve_values.plot_efficiency_vs_Q(ax=ax3[0,0])
        q_curve_values.plot_power_vs_Q(ax=ax3[1,0])

        n_curve_values = HillChart()
        n_curve_values.read_hill_chart_values(self.datapath)
        n_curve_values.prepare_hill_chart_data()
        n_curve_values.slice_hill_chart_data(selected_n11=None, selected_Q11=BEP_data.Q11[0])
        n_curve_values.calculate_cases([2, 4], BEP_data.Q[0], BEP_data.D[0])
        n_curve_values.plot_efficiency_vs_n(ax=ax3[0,1])
        n_curve_values.plot_power_vs_n(ax=ax3[1,1])
        
        plt.show(block=False)
