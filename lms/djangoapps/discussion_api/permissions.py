"""
Discussion API permission logic
"""


def _is_user_author_or_privileged(cc_content, context):
    """
    Check if the user is the author of a content object or a privileged user.

    Returns:
        Boolean
    """
    return (
        context["is_requester_privileged"] or
        context["cc_requester"]["id"] == cc_content["user_id"]
    )


def get_thread_editable_fields(cc_thread, context):
    """
    Get the list of editable fields for the given thread in the given context
    """
    ret = {"following", "voted"}
    if _is_user_author_or_privileged(cc_thread, context):
        ret |= {"topic_id", "type", "title", "raw_body"}
    return ret


def get_comment_editable_fields(cc_comment, context):
    """
    Get the list of editable fields for the given comment in the given context

    cc_comment can be None to get permissions for a newly created comment
    """
    ret = {"voted"}
    if _is_user_author_or_privileged(cc_comment, context):
        ret |= {"raw_body"}
    if _is_user_author_or_privileged(context["thread"], context):
        ret |= {"endorsed"}
    return ret


def can_delete(cc_content, context):
    """Returns True iff the requester is allowed to delete the given content"""
    return _is_user_author_or_privileged(cc_content, context)
