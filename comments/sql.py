
CHILDREN_SQL = '''
with parents as (
    select c.*
        , (select max(ct.id) id
           from django_content_type ct
           where ct.app_label = 'comments' and ct.model = 'comment') as self_content_type
    from comments_comment c
    where c.id = %(id)s
),
users as (
     select id, username
      from auth_user
),
ordered_data as (
    select c.id, c.text, c.parent_id, c.content_type_id as content_type, c.object_id, c.parent_id as parent
        , c.created_at, c.updated_at, p.self_content_type, to_json(u.*) as user
    from comments_comment c
        join users u on u.id = c.user_id
        join parents p on p.tree_id = c.tree_id
              and c.lft > p.lft
              and c.lft < p.rght
    ORDER BY c.tree_id ASC, c.lft ASC
)
select to_json(o.*)
from ordered_data o;
'''

REPORT_SQL = '''
with parents as (
    select c.*
        , (select max(ct.id) id
           from django_content_type ct
           where ct.app_label = 'comments' and ct.model = 'comment') as self_content_type    
    from comments_comment c
    where c.content_type_id = %(content_type_id)s
      and c.object_id = %(object_id)s
      and (c.user_id = %(user_id)s or %(user_id)s is null)
      and (c.created_at >= %(created_at__gte)s or %(created_at__gte)s is null)
      and (c.created_at < %(created_at__lt)s or %(created_at__lt)s is null)
),
users as (
     select id, username
      from auth_user
),
ordered_data as (
    select c.id, c.text, c.parent_id, c.content_type_id as content_type, c.object_id, c.parent_id as parent
            , c.created_at, c.updated_at, p.self_content_type, to_json(u.*) as user
    from comments_comment c
      join users u on u.id = c.user_id
      join parents p on p.tree_id = c.tree_id
          and c.lft >= p.lft
          and c.lft < p.rght
    where (c.user_id = %(user_id)s or %(user_id)s is null)
        and (c.created_at >= %(created_at__gte)s or %(created_at__gte)s is null)
        and (c.created_at < %(created_at__lt)s or %(created_at__lt)s is null)
    ORDER BY c.tree_id ASC, c.lft ASC
)
select to_json(o.*)
from ordered_data o;
'''

SUBSCRIBERS_SQL = '''
with comments as (
    select parent.*
    from comments_comment c
      join comments_comment parent on parent.tree_id = c.tree_id
        and parent.lft <= c.lft
        and parent.rght >= c.rght
    where c.id = %(id)s
),
subscribed_users as (
    select distinct s.user_id
    from comments c
      join comments_subscribe s on s.content_type_id = c.content_type_id
        and c.object_id = s.object_id
)
select to_json(u.*)
from subscribed_users u;
'''