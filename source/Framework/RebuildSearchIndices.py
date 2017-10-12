from source.models.NdbClasses import Tag, Stream
from google.appengine.api import search
import Framework_Helpers as fh


def rebuild_stream_index():
    # get all existing stream names
    all_streams = Stream.get_all()

    # define new tag search index name
    if fh.get_stream_index_name() == "stream_index":
        new_index_name = "stream_index_alt"
    else:
        new_index_name = "stream_index"

    # add all tags to new index
    for stream in all_streams:
        fh.searchablize_tag_or_stream(stream, new_index_name, {})

    # switch primary search
    old_index_name = fh.get_stream_index_name()
    fh.set_stream_index_name(new_index_name)

    # empty old index
    empty_index(old_index_name)


def rebuild_tag_index():
    # get all existing tags
    all_tags = Tag.get_all()

    # define new tag search index name
    if fh.get_tag_index_name() == "tag_index":
        new_index_name = "tag_index_alt"
    else:
        new_index_name = "tag_index"

    # add all tags to new index
    for tag in all_tags:
        fh.searchablize_tag_or_stream(tag, new_index_name, {})

    # switch primary search
    old_index_name = fh.get_tag_index_name()
    fh.set_tag_index_name(new_index_name)

    # empty old index
    empty_index(old_index_name)


def empty_index(index_name):
    index = search.Index(name=index_name, namespace=fh.search_index_namespace)
    try:
        while True:
            # until no more documents, get a list of documents,
            # constraining the returned objects to contain only the doc ids,
            # extract the doc ids, and delete the docs.
            document_ids = [document.doc_id for document in index.get_range(ids_only=True)]
            if not document_ids:
                break
            index.delete(document_ids)
    except search.DeleteError:
        msg = 'Error removing exceptions'
