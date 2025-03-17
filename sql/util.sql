SELECT id,
       repository_id                                   as repository,
       text                                            as comment,
       CASE WHEN is_td = TRUE THEN 'yes' ELSE 'no' END AS satd,
       td_type                                         as type
from comment
where is_random = TRUE order by id;

select td_type, count(id)
from comment
where td_type is not null
group by td_type;