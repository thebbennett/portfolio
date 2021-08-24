with

all_weeks as (
  select * from {{ref('all_weeks')}}
),

full_action_history as (
  select * from {{ref('full_action_history')}}
),

members as (
  select * from {{ref('members')}}
),

became_member_week as (
  select
  	vanid,
    date_trunc('week', became_member_at) as first_active_week
  from members
),

spined as (
  select
    vanid,
    all_weeks.date_week

  from became_member_week
  left join all_weeks
  	on all_weeks.date_week >= became_member_week.first_active_week
),

member_active_weeks as (
  select
    date_trunc('week', action_at) as action_week,
    vanid,
    max(1) as took_action_this_week
  from members
  left join full_action_history using(vanid)
  where action_at >= became_member_at
  group by 1,2
),

filled as (
  select
  	spined.date_week,
  	spined.vanid,
  	coalesce(member_active_weeks.took_action_this_week, 0) as is_active_this_week,
    max(is_active_this_week) over (
              partition by spined.vanid
              order by spined.date_week
              rows between 24 preceding and current row
          ) as is_active_6_months

  from spined
  left join member_active_weeks
  	on spined.date_week::date = member_active_weeks.action_week::date
  	and spined.vanid = member_active_weeks.vanid

)
select * from filled
