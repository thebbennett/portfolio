with metrics_members as (
    select * from {{ ref('metrics_members') }}
),

final as (
    select
        date_week,
        sum(is_active_this_week::integer) as weekly_active_members,
        sum(is_active_6_months::integer) as six_months_active_members

    from metrics_members

    group by 1
)

select * from final
order by date_week
