import seaborn as sns
import xarray as xr
from copy import deepcopy
import panel as pn
import logging
from bencher.bench_cfg import PltCfgBase, BenchCfg, describe_benchmark
from bencher.bench_vars import ParametrizedOutput, ResultVar
from bencher.optuna_conversions import collect_optuna_plots
import bencher.plotting_functions as plt_func
from plotting_functions import PltCntCfg


class BenchPlotter:
    @staticmethod
    def plot(bench_cfg: BenchCfg, main_tab=None, append_cols=None) -> pn.pane:
        """Given the dataset result of a benchmark run, automatically dedeuce how to plot the data based on the types of variables that were sampled

        Args:
            bench_cfg (BenchCfg): Information on how the benchmark was sampled and the resulting data

        Returns:
            pn.pane: A panel containing plot results
        """

        if main_tab is None:
            main_tab = pn.Tabs(tabs_location="left")

        if len(bench_cfg.result_vars) == 0:
            tabs = pn.Column(name=bench_cfg.title)
            tabs.append(pn.pane.Markdown(f"{bench_cfg.description}"))

        else:
            plot_cols = pn.Column(name="Plots View")
            plot_cols.append(
                pn.pane.Markdown(f"# {bench_cfg.title}\n{bench_cfg.description}")
            )
            benmark_str = describe_benchmark(bench_cfg)
            plot_cols.append(pn.pane.Markdown(f"{benmark_str}"))
            if bench_cfg.over_time:
                if len(bench_cfg.ds.coords["over_time"]) > 1:
                    plot_cols.append(pn.pane.Markdown("## Results Over Time"))
                    plot_cols.append(BenchPlotter.plot_results_row(bench_cfg))
                else:
                    plot_cols.append(
                        pn.pane.Markdown(
                            "Results over time needs at least 2 time snapshots to plot"
                        )
                    )

            plot_cols.append(pn.pane.Markdown("## Most Recent Results"))
            if bench_cfg.over_time:
                bench_deep = deepcopy(
                    bench_cfg
                )  # TODO do this in the future without copying
                bench_deep.over_time = False
                bench_deep.iv_time = []
                last_time = bench_deep.ds.coords["over_time"][-1]
                try:
                    bench_deep.ds = bench_deep.ds.sel(over_time=last_time)
                    plot_cols.append(BenchPlotter.plot_results_row(bench_deep))
                except ValueError as e:
                    warning = f"failed to load historical data: {e}"
                    plot_cols.append(pn.pane.Markdown(warning))
                    logging.warn(warning)

            else:
                plot_cols.append(BenchPlotter.plot_results_row(bench_cfg))

            if bench_cfg.use_optuna:
                plot_cols.extend(collect_optuna_plots(bench_cfg))

            if append_cols is not None:
                plot_cols.extend(append_cols)
            plot_cols.append(pn.pane.Markdown(f"{bench_cfg.post_description}"))

            tabs = pn.Tabs(plot_cols, name=bench_cfg.title)

            if bench_cfg.serve_xarray:
                tabs.append(
                    pn.Column(
                        pn.pane.Markdown(
                            """This page shows the with the inputs of the parameter sweep and the results in its native N-D xarray dataset format."""
                        ),
                        bench_cfg.ds,
                        name="Xarray Dataset View",
                    )
                )
            if bench_cfg.serve_pandas:
                tabs.append(
                    pn.Column(
                        pn.pane.Markdown(
                            """This page shows the with the inputs of the parameter sweep and the results as a pandas multiindex."""
                        ),
                        bench_cfg.ds.to_dataframe(),
                        name="Pandas Dataframe MultiIndex View",
                    )
                )

                tabs.append(
                    pn.Column(
                        pn.pane.Markdown(
                            """This page shows the with the inputs of the parameter sweep and the results as a flattened padas dataframe."""
                        ),
                        bench_cfg.ds.to_dataframe().reset_index(),
                        name="Pandas Dataframe Flattened View",
                    )
                )

        main_tab.append(tabs)
        main_tab.servable()

        return main_tab

    @staticmethod
    def plot_results_row(bench_cfg: BenchCfg) -> pn.Row:
        """Given a BenchCfg, plot each result variable and add to a panel row

        Args:
            bench_cfg (BenchCfg): The BenchCfg to plot

        Returns:
            pn.Row: A panel row with plots in it
        """
        plot_rows = pn.Row(name=bench_cfg.bench_name)
        plt_cnt_cfg = PltCntCfg.from_benchCfg(bench_cfg)
        for rg in bench_cfg.result_groups:
            for rv in bench_cfg.result_vars:
                plot_rows.append(
                    BenchPlotter.plot_result_variable_group(bench_cfg, rg, plt_cnt_cfg)
                )
        for rv in bench_cfg.result_vars:
            plot_rows.append(
                BenchPlotter.plot_result_variable(bench_cfg, rv, plt_cnt_cfg)
            )

        return plot_rows

    @staticmethod
    def plot_result_variable(
        bench_cfg: BenchCfg, rv: ParametrizedOutput, plt_cnt_cfg: PltCntCfg
    ) -> pn.Column:
        """This method returns a single plot based on 1 result variable and a set of input variables.  It dedeuces the correct plot type by passing it to several configuration functions that operate on the number of inputs

        Args:
            bench_cfg (BenchCfg): A config of the input vars
            rv (ParametrizedOutput): a config of the result variable
            plt_cnt_cfg (PltCntCfg): A config of how many input types there are

        Raises:
            FileExistsError: If there are file naming conflicts

        Returns:
            PlotResult: A summary of all the data used to generate a plot
        """
        surf_col = pn.Column()

        sns_cfg = PltCfgBase()
        sns_cfg.y = (
            rv.name
        )  # by default the result variable is always plotted on the y axis

        if plt_cnt_cfg.float_cnt < 2:
            # set a marker for time series to its easy to see the measurment points
            if bench_cfg.over_time:
                sns_cfg.marker = "."
            if plt_cnt_cfg.float_cnt == 0:
                sns_cfg = BenchPlotter.plot_float_cnt_0(sns_cfg, plt_cnt_cfg)
            elif plt_cnt_cfg.float_cnt == 1:
                sns_cfg = BenchPlotter.plot_float_cnt_1(sns_cfg, plt_cnt_cfg)
            sns_cfg = BenchPlotter.get_axes_and_title(rv, sns_cfg, plt_cnt_cfg)
            surf_col.append(plt_func.plot_sns(bench_cfg, rv, sns_cfg))
        else:
            if plt_cnt_cfg.float_cnt == 2:
                xr_cfg = BenchPlotter.plot_float_cnt_2(plt_cnt_cfg, rv, bench_cfg.debug)
                if plt_cnt_cfg.cat_cnt == 0:
                    surf_col.append(plt_func.plot_surface_plotly(bench_cfg, rv, xr_cfg))
                else:
                    try:
                        surf_col.append(
                            plt_func.plot_surface_holo(bench_cfg, rv, xr_cfg)
                        )
                    except (TypeError, KeyError) as e:
                        surf_col.append(
                            pn.pane.Markdown(
                                "3D (cat,float,cat) inputs -> (float) output plots are not supported yet"
                            )
                        )

            elif plt_cnt_cfg.float_cnt == 3:
                xr_cfg = BenchPlotter.plot_float_cnt_3(
                    sns_cfg, plt_cnt_cfg, bench_cfg.debug
                )
                if plt_cnt_cfg.cat_cnt < 1:
                    if type(rv) == ResultVar:
                        surf_col.append(
                            plt_func.plot_volume_plotly(bench_cfg, rv, xr_cfg)
                        )
                    else:
                        surf_col.append(
                            plt_func.plot_cone_plotly(bench_cfg, rv, xr_cfg)
                        )
                else:
                    surf_col.append(
                        pn.pane.Markdown(
                            "3D (float,float,cat) inputs -> (float) output plots are not supported yet"
                        )
                    )
            else:
                surf_col.append(
                    pn.pane.Markdown(
                        "4D and higher continous variable sweeps plots are not currently supported.  2D continous inputs + an arbirary number of categorical input are supported.  Please consider relocating to a universe with >4 spatial dimensions so that you have the nessisary physiology to view 4D tensors. "
                    )
                )

        return surf_col
