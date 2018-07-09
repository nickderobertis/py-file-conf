from functools import partial
from typing import Union, Sequence, List, Callable
import datetime
from copy import deepcopy

from dero.manager.basemodels.pipeline import Pipeline
from dero.manager.data.models.source import DataSource
from dero.manager.data.models.merge import DataMerge, MergeOptions, LastMergeFinishedException
from dero.manager.selector.models.itemview import ItemView

DataSourceOrPipeline = Union[DataSource, 'DataPipeline']
DataSourcesOrPipelines = Sequence[DataSourceOrPipeline]
MergeOptionsList = Sequence[MergeOptions]
DataMerges = List[DataMerge]


class DataPipeline(Pipeline):

    def __init__(self, data_sources: DataSourcesOrPipelines=None, merge_options_list: MergeOptionsList=None,
                 outpath=None, post_merge_cleanup_func=None, name: str=None, **cleanup_kwargs):
        self.data_sources = data_sources
        self.merge_options_list = merge_options_list
        self._merge_index = 0
        self._set_cleanup_func(post_merge_cleanup_func, **cleanup_kwargs)
        self.outpath = outpath
        self.name = name

    def execute(self):
        while True:
            try:
                self.next_merge()
            except LastMergeFinishedException:
                break

        if self.has_post_merge_cleanup_func:
            self.df = self.post_merge_cleanup_func(self.df)
        self.output()

        return self.df

    def next_merge(self):
        # On first merge, set df
        if self._merge_index == 0:
            self._set_df_from_first_merge()

        self._merge()

    def output(self, outpath=None):
        if outpath:
            self._output(outpath)
        elif self.outpath:
            self._output(self.outpath)

    def summary(self, *summary_args, summary_method: str=None, summary_function: Callable=None,
                             summary_attr: str=None, **summary_method_kwargs):
        for merge in self.merges:
            merge.summary(
                *summary_args,
                summary_method=summary_method,
                summary_function=summary_function,
                summary_attr=summary_attr,
                **summary_method_kwargs
            )

    def _output(self, outpath=None):
        self.df.to_csv(outpath, index=False, encoding='utf8')

    def _merge(self):
        try:
            print(f'Now running merge {self._merge_index + 1}: {self.merges[self._merge_index]}')
        except IndexError:
            raise LastMergeFinishedException

        self.merges[self._merge_index].merge()

        # Set current df to result of merge
        self.df = self.merges[self._merge_index].result.df

        self._merge_index += 1

        # TODO: add output considering path in merge options

    @property
    def merges(self):
        try:
            return self._merges
        except AttributeError:
            self._set_merges()

        return self._merges

    # Following properties exist to recreate merges if data sources or merge options are overridden
    # by user

    @property
    def data_sources(self):
        return self._data_sources

    @data_sources.setter
    def data_sources(self, data_sources: DataSourcesOrPipelines):
        self._data_sources = data_sources
        # only set merges if previously set. otherwise no need to worry about updating cached result
        if hasattr(self, '_merges'):
            self._set_merges()

    @property
    def merge_options_list(self):
        return self._merge_options_list

    @merge_options_list.setter
    def merge_options_list(self, merge_options_list: MergeOptionsList):
        self._merge_options_list = merge_options_list
        # only set merges if previously set. otherwise no need to worry about updating cached result
        if hasattr(self, '_merges'):
            self._set_merges()

    def _set_merges(self):
        self._touch_data_sources()
        self._merges = self._create_merges(self.data_sources, self.merge_options_list)

    def _create_merges(self, data_sources: DataSourcesOrPipelines, merge_options_list: MergeOptionsList):
        merges = _get_merges(data_sources[0], data_sources[1], merge_options_list[0])
        if len(merge_options_list) == 1:
            return merges

        for i, merge_options in enumerate(merge_options_list[1:]):
            merges += _get_merges(merges[-1].result, data_sources[i + 2], merge_options)

        return merges

    def _set_df_from_first_merge(self):
        self.df = self.merges[0].data_sources[0].df

    def _set_cleanup_func(self, post_merge_cleanup_func, **cleanup_kwargs):
        if post_merge_cleanup_func is not None:
            self.has_post_merge_cleanup_func = True
            self.post_merge_cleanup_func = partial(post_merge_cleanup_func, **cleanup_kwargs)
        else:
            self.has_post_merge_cleanup_func = False

    @property
    def last_modified(self):
        self._touch_data_sources()
        return max([source.last_modified for source in self.data_sources])

    @property
    def source_last_modified(self):
        most_recent_time = datetime.datetime(1900, 1, 1)
        for i, source in enumerate(self.data_sources):
            if source.last_modified > most_recent_time:
                most_recent_time = source.last_modified
                most_recent_index = i

        return self.data_sources[most_recent_index]

    def copy(self):
        return deepcopy(self)

    def _touch_data_sources(self):
        """
        Data sources may be passed using dero.manager.Selector, in which case they
        are dero.manager.selector.models.itemview.ItemView objects. _get_merges uses isinstance, which will
        return ItemView, and so won't work correctly. By accessing the .item proprty of the ItemView,
        we get the original item back
        Returns:

        """
        real_data_sources = []
        for data_source_or_view in self.data_sources:
            if isinstance(data_source_or_view, ItemView):
                real_data_sources.append(data_source_or_view.item)
            else:
                real_data_sources.append(data_source_or_view)
        self.data_sources = real_data_sources


def _get_merges(data_source_1: DataSourceOrPipeline, data_source_2: DataSourceOrPipeline,
                merge_options: MergeOptions) -> DataMerges:
    """
    Creates a list of DataMerge objects from a paring of two DataSource objects, a DataSource and a DataPipeline,
    or two DataPipeline objects.
    :param data_source_1: DataSource or DataPipeline
    :param data_source_2: DataSource or DataPipeline
    :param merge_options: MergeOptions
    :return: list of DataMerge objects
    """
    merges = []
    final_merge_sources = []
    # Add any pipeline merges first, as the results from the pipeline must be ready before we can merge the results
    # to other data sources or pipeline results
    if isinstance(data_source_1, DataPipeline):

        # TODO: implement cleanup funcs in pipelines of pipelines
        if data_source_1.has_post_merge_cleanup_func:
            raise NotImplementedError(f'no handling yet for post merge cleanup function in {data_source_1}')

        merges += data_source_1.merges
        pipeline_1_result = data_source_1.merges[-1].result
        final_merge_sources.append(pipeline_1_result) # result of first pipeline will be first source in final merge
    if isinstance(data_source_2, DataPipeline):

        # TODO: implement cleanup funcs in pipelines of pipelines
        if data_source_2.has_post_merge_cleanup_func:
            raise NotImplementedError(f'no handling yet for post merge cleanup function in {data_source_2}')

        merges += data_source_2.merges
        pipeline_2_result = data_source_2.merges[-1].result # result of second pipeline will be second source in final merge

    if isinstance(data_source_1, DataSource):
        final_merge_sources.append(data_source_1)

    # Now final merge source 1 is filled, may add 2
    if isinstance(data_source_2, DataPipeline):
        final_merge_sources.append(pipeline_2_result)
    elif isinstance(data_source_2, DataSource):
        final_merge_sources.append(data_source_2)

    # Add last (or only) merge
    merges.append(DataMerge(final_merge_sources, merge_options))

    return merges


