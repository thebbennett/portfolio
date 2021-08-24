with

metrics_members as (
  select * from {{ref('metrics_members')}}

),

active_members as (
  select * from metrics_members
  where is_active_6_months = 1
)

select * from active_members
