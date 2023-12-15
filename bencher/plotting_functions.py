# from bencher.bench_cfg import BenchCfg
# from bencher.results.bench_result import BenchResult


# def wrap_long_time_labels(bench_res: BenchResult) -> BenchCfg:
#     """Takes a benchCfg and wraps any index labels that are too long to be plotted easily

#     Args:
#         bench_cfg (BenchCfg):

#     Returns:
#         BenchCfg: updated config with wrapped labels
#     """
#     if bench_cfg.over_time:
#         if bench_cfg.ds.coords["over_time"].dtype == np.datetime64:
#             # plotly catastrophically fails to plot anything with the default long string representation of time, so convert to a shorter time representation
#             bench_cfg.ds.coords["over_time"] = [
#                 pd.to_datetime(t).strftime("%d-%m-%y %H-%M-%S")
#                 for t in bench_cfg.ds.coords.coords["over_time"].values
#             ]
#             # wrap very long time event labels because otherwise the graphs are unreadable
#         if bench_cfg.time_event is not None:
#             bench_cfg.ds.coords["over_time"] = [
#                 "\n".join(wrap(t, 20)) for t in bench_cfg.ds.coords["over_time"].values
#             ]
#     return bench_cfg
