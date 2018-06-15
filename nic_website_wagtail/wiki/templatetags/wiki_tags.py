from django import template
from django.template.defaulttags import token_kwargs


from django.utils.encoding import force_text

register = template.Library()


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


def menu(context, parent, calling_page=None):
    menuitems = parent.get_children().live().in_menu()
    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


def menu_children(context, parent):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the top menu items - the immediate children of the parent page
# The has_menu_children method is necessary because the bootstrap menu requires
# a dropdown class to be applied to a parent
@register.inclusion_tag('wiki/tags/top_menu.html', takes_context=True)
def top_menu(context, parent, calling_page=None):
    menuitems = parent.get_children().live().in_menu()
    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)
        # We don't directly check if calling_page is None since the template
        # engine can pass an empty string to calling_page
        # if the variable passed as calling_page does not exist.
        menuitem.active = (calling_page.url.startswith(menuitem.url)
                           if calling_page else False)
    return {
        'calling_page': calling_page,
        'menuitems': menuitems,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves the children of the top menu items for the drop downs
@register.inclusion_tag('wiki/tags/top_menu_children.html', takes_context=True)
def top_menu_children(context, parent):
    menuitems_children = parent.get_children()
    menuitems_children = menuitems_children.live().in_menu()
    return {
        'parent': parent,
        'menuitems_children': menuitems_children,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# Retrieves all live pages which are children of the calling page
# for standard index listing
@register.inclusion_tag(
    'wiki/tags/standard_index_listing.html',
    takes_context=True
)
def standard_index_listing(context, calling_page):
    pages = calling_page.get_children().live()
    return {
        'pages': pages,
        # required by the pageurl tag that we want to use within this template
        'request': context['request'],
    }


# class IncludeBlockNode(template.Node):
#     def __init__(self, block_var, extra_context, use_parent_context):
#         self.block_var = block_var
#         self.extra_context = extra_context
#         self.use_parent_context = use_parent_context

#     def render(self, context):
#         try:
#             value = self.block_var.resolve(context)
#         except template.VariableDoesNotExist:
#             return ''

#         if hasattr(value, 'render_as_block'):
#             if self.use_parent_context:
#                 new_context = context.flatten()
#             else:
#                 new_context = {}

#             if self.extra_context:
#                 for var_name, var_value in self.extra_context.items():
#                     new_context[var_name] = var_value.resolve(context)

#             return value.render_as_block(context=new_context)
#         else:
#             return force_text(value)


# @register.tag
# def wiki_include_block(parser, token):
#     """
#     Render the passed item of StreamField content, passing the current template context
#     if there's an identifiable way of doing so (i.e. if it has a `render_as_block` method).
#     """
#     tokens = token.split_contents()

#     try:
#         tag_name = tokens.pop(0)
#         block_var_token = tokens.pop(0)
#     except IndexError:
#         raise template.TemplateSyntaxError("%r tag requires at least one argument" % tag_name)

#     block_var = parser.compile_filter(block_var_token)

#     if tokens and tokens[0] == 'with':
#         tokens.pop(0)
#         extra_context = token_kwargs(tokens, parser)
#     else:
#         extra_context = None

#     use_parent_context = True
#     if tokens and tokens[0] == 'only':
#         tokens.pop(0)
#         use_parent_context = False

#     if tokens:
#         raise template.TemplateSyntaxError("Unexpected argument to %r tag: %r" % (tag_name, tokens[0]))

#     return IncludeBlockNode(block_var, extra_context, use_parent_context)
